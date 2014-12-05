from numpy import array, zeros
from numpy import mean, var
from random import sample
from pandas import read_csv
from sklearn.svm import SVC

# Very small area
nw_corner = array([396210, 4175310])
se_corner = array([404460, 4167150])

# Calculate file names
fname_post = '_{0}_{1}_{2}_{3}.'.format(nw_corner[0], nw_corner[1], se_corner[0], se_corner[1])
fname_template = 'tmp/{0}' + fname_post + '{1}'

# Organize data
explanatory_variables = [
    'month',
    'b1_ref', 'b1_var',
    'b2_ref', 'b2_var',
    'b3_ref', 'b3_var',
    'b4_ref', 'b4_var',
    'b5_ref', 'b5_var',
    'b6_ref', 'b6_var',
    'b7_ref', 'b7_var',
]
outcome_variable = 'CropTruth'
data_set = read_csv(fname_template.format('field_data_truth', 'csv'))
data_matrix = data_set[explanatory_variables].as_matrix()
outcome_truth = data_set[outcome_variable].as_matrix()


# Select random indices for each trial
n_trials = 100
train_fraction = 0.8
trial_outcomes = zeros(n_trials)
data_length = data_set.shape[0]
num_samples = int(data_length * train_fraction)
num_tests = data_length - num_samples
all_indices = range(data_length)

# Evaluate try a few time to see how well the crops can be predicted.
for trial in range(n_trials):
    # Divide data array into training set and
    training_indices = sample(all_indices, num_samples)
    training_indices.sort()
    test_indices = [x for x in all_indices if x not in training_indices]
    test_indices.sort()

    # Create the training data set
    sampled_training_data = data_matrix[training_indices]
    sampled_training_outcomes = outcome_truth[training_indices]
    sampled_test_data = data_matrix[test_indices]
    sampled_test_outcomes = outcome_truth[test_indices]

    # Predict outcomes and save values
    model = SVC()
    model.fit(sampled_training_data, sampled_training_outcomes)
    modeled_outcome = model.predict(sampled_test_data)
    #print(modeled_outcome)

    # Figure out how well the model has done
    percent_correct = sum(modeled_outcome == sampled_test_outcomes) / num_tests
    trial_outcomes[trial] = percent_correct

print('After {0} trials, correct outcome stats:\n\tMean: {1}\n\tVar:  {2}'.format(
    n_trials, mean(trial_outcomes), var(trial_outcomes)
))

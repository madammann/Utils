import os
import tensorflow as tf

@tf.function
def compute_ppo_loss(observations, targets, actions, returns, advantages, prob_old_policy, old_value):
    # Compute the new policy probabilities
    policy = tf.nn.softmax(policy_logits, axis=-1)
    old_policy = tf.nn.softmax(old_policy_logits, axis=-1)
    
    # Get the probabilities of the selected actions
    policy_prob = tf.reduce_sum(policy * tf.one_hot(actions, policy_logits.shape[-1]), axis=-1)
    old_policy_prob = tf.reduce_sum(old_policy * tf.one_hot(actions, policy_logits.shape[-1]), axis=-1)
    
    # Compute the probability ratio
    ratio = policy_prob / (old_policy_prob + 1e-10)
    
    # Compute the clipped surrogate objective
    clip_adv = tf.clip_by_value(ratio, 1.0 - clip_epsilon, 1.0 + clip_epsilon) * advantages
    actor_loss = -tf.reduce_mean(tf.minimum(ratio * advantages, clip_adv))
    
    # Compute the value function loss
    value_loss = tf.reduce_mean(tf.square(returns - values))
    
    # Compute the entropy bonus
    log_policy = tf.nn.log_softmax(policy_logits, axis=-1)
    entropy = -tf.reduce_sum(policy * log_policy, axis=-1)
    entropy_bonus = tf.reduce_mean(entropy)
    
    # Total PPO loss
    total_loss = actor_loss + c1 * value_loss - c2 * entropy_bonus
    
    return combined_loss, actor_loss, critic_loss, kld

def train_step(*args, **kwargs):
    with tf.GradientTape() as tape:
        res = compute_ppo_loss(*args, **kwargs)
        
    gradients = tape.gradient(combined_loss, model.parameters())
    optimizer.apply_gradients(zip(gradients, model.parameters()))

    return None

def training_loop(model, optimizer, dataset, epoch, dataset_repeats=4, **hyperparams):
    '''
    ADD
    '''

    KEYS = ('observations', 'targets', 'actions', 'returns', 'advantages', 'probs_log', 'values')
    for observations, targets, actions, returns, advantages, prob_old_policy, old_value in data_set(*KEYS, n=dataset_repeats):
        res = train_step(observations, targets, actions, returns, advantages, prob_old_policy, old_value)
        if kld < 0.9:
            pass

    # model.save()
    # print()
    # return None

def sampling_loop(model, **hyperparams):
    trajectories = {
        'observations' : [],
        'targets' : [],
        'actions' : [],
        'returns' : []
    }

    while True:
        pass
    
    trajectories = None
    
    buffer = EpisodeBuffer(trajectories)

    return buffer

def eval_loop(path, model, **hyperparams):
    '''
    ADD
    '''
    last_episode = 1
    folders = os.listdir(f'{path}\\screenshots\\')
    if any([p.startswith('episode_') for p in folders]):
        last_episode = max([int(p.split('_')[1]) for p in folders if p.isdir() and p.startswith('episode_')])
    paths = [f'{path}\\screenshots\\episode_{i}' for i in range(last_episode, last_episode+hyperparams['num_envs'])]
    
    while True:
        pass
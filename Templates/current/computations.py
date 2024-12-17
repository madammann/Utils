import tensorflow as tf

@tf.function
def compute_advantages(rewards, values, gamma, lam):
    advantages = tf.TensorArray(dtype=tf.float32, size=0, dynamic_size=True)
    advantage = 0.0

    for t in tf.range(tf.shape(rewards)[0] - 1, -1, -1):
        delta = rewards[t] + gamma * values[t + 1] - values[t]
        advantage = delta + gamma * lam * advantage
        advantages = advantages.write(t, advantage)
    
    return advantages.stack()

@tf.function
def log_probabilities(actions, logits):
    actions = tf.cast(actions, tf.int32)
    action_probs = tf.nn.softmax(logits)
    log_probs = tf.math.log(action_probs + 1e-10)
    return tf.gather(log_probs, actions, batch_dims=1)


@tf.function
def entropy_regularization(logits):
    action_probs = tf.nn.softmax(logits)
    log_probs = tf.nn.log_softmax(logits)
    entropy = -tf.reduce_sum(action_probs * log_probs, axis=-1)
    return entropy


@tf.function
def ppo_update(model, old_log_probs, observations, actions, advantages, clip_ratio, optimizer):
    with tf.GradientTape() as tape:
        logits = model(observations)
        log_probs = log_probabilities(actions, logits)
        ratio = tf.exp(log_probs - old_log_probs)
        clipped_ratio = tf.clip_by_value(ratio, 1.0 - clip_ratio, 1.0 + clip_ratio)
        loss = -tf.reduce_mean(tf.minimum(ratio * advantages, clipped_ratio * advantages))
    
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    return loss

import tensorflow as tf

def compute_entropy_loss(policy_logits):
    """
    Computes the entropy loss for a given policy.

    Arguments:
    policy_logits -- Tensor of shape [batch_size, num_actions], the logits of the policy network

    Returns:
    entropy_loss -- Tensor representing the entropy loss
    """
    policy = tf.nn.softmax(policy_logits, axis=-1)
    log_policy = tf.nn.log_softmax(policy_logits, axis=-1)
    entropy = -tf.reduce_sum(policy * log_policy, axis=-1)
    entropy_loss = -tf.reduce_mean(entropy)
    return entropy_loss


import tensorflow as tf

def compute_ppo_loss(policy_logits, old_policy_logits, actions, advantages, returns, values, clip_epsilon=0.2, c1=0.5, c2=0.01):
    """
    Computes the PPO loss for the actor and critic.

    Arguments:
    policy_logits -- Tensor of shape [batch_size, num_actions], current policy logits
    old_policy_logits -- Tensor of shape [batch_size, num_actions], old policy logits
    actions -- Tensor of shape [batch_size], actions taken by the agent
    advantages -- Tensor of shape [batch_size], advantage estimates
    returns -- Tensor of shape [batch_size], actual returns
    values -- Tensor of shape [batch_size], predicted values
    clip_epsilon -- Clipping parameter for PPO (default 0.2)
    c1 -- Weight for the value loss (default 0.5)
    c2 -- Weight for the entropy bonus (default 0.01)

    Returns:
    total_loss -- Scalar tensor representing the total PPO loss
    """
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
    
    return total_loss

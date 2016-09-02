import lasagne
import theano
import theano.tensor as T
import numpy as np
from six.moves import cPickle
from lasagne.layers import InputLayer, DenseLayer, Conv2DLayer, batch_norm, ElemwiseSumLayer

def iterate_minibatches(inputs, targets, batchsize, shuffle=False):
    assert len(inputs) == len(targets)
    print(len(targets))
    if shuffle:
        indices = np.arange(len(inputs))
        np.random.shuffle(indices)
    for start_idx in range(0, len(inputs) - batchsize + 1, batchsize):
        if shuffle:
            excerpt = indices[start_idx:start_idx + batchsize]
        else:
            excerpt = slice(start_idx, start_idx + batchsize)
        yield inputs[excerpt], targets[excerpt]

def save_model(network):
    np.savez('conv-model.npz', *lasagne.layers.get_all_param_values(network))

def build_model():
    input_var = T.tensor4('X')
    from lasagne.nonlinearities import leaky_rectify, softmax
    network = lasagne.layers.InputLayer(shape=(None, 6, 8, 8),
                                        input_var=input_var)
    network = Conv2DLayer(network, 16, 7, stride = 1, pad = 'same')
    network = build_residual_layer(network, 16, 2)
    network = build_resize_layer(network, 32)
    network = build_residual_layer(network, 32, 2)
    network = build_resize_layer(network, 64)
    network = build_residual_layer(network, 64, 2)
    network = build_resize_layer(network, 128)
    network = build_residual_layer(network, 128, 2)
    network = DenseLayer(lasagne.layers.DropoutLayer(network, 0.2), 4096, nonlinearity=softmax)
    return input_var, network

def build_residual_layer(network, num_filters, num_elements):
    original = network
    #like an 8x8 but with about half the parameters... maybe...
    for i in xrange(num_elements):
        network = Conv2DLayer(network, num_filters, 7, stride = 1, pad='same')
        network = batch_norm(network)
    return ElemwiseSumLayer([original, network])

def build_resize_layer(network, num_filters_out):
    #1x1 convolutions
    network = Conv2DLayer(network, num_filters_out, 1, stride = 1, pad='same')
    network = batch_norm(network)
    return network

def build_network_from_model(filename):
    input_var, network = build_model()
    with np.load(filename) as f:
        param_values = [f['arr_%d' % i] for i in range(len(f.files))]
    lasagne.layers.set_all_param_values(network, param_values)
    return input_var, network

def test(input_var, network):
    # create Theano variables for input and target minibatch
    target_var = T.matrix('y')

    test_x = np.array(np.ma.load("conv-white-chess-testing-input.data"))

    test_y = np.squeeze(np.array(np.ma.load("white-chess-testing-output.data")))

    test_prediction = lasagne.layers.get_output(network, deterministic=True)
    test_loss = lasagne.objectives.categorical_crossentropy(test_prediction,
                                                                target_var)
    test_loss = test_loss.mean()
    val_fn = theano.function([input_var, target_var], test_loss)
    view_fn = theano.function([input_var], (T.argmax(test_prediction, axis=1), test_prediction[0,T.argmax(test_prediction, axis=1)]))

    # use trained network for predictions
    test_err = 0
    test_batches = 0
    for batch in iterate_minibatches(test_x, test_y, 1, shuffle=False):
        inputs, targets = batch
        err = val_fn(inputs, targets)
        print view_fn(inputs)
        test_err += err
        test_batches += 1

    print test_err
    print float(test_err)/test_batches
    print test_batches



def train(input_var, network):
    # create Theano variables for input and target minibatch
    target_var = T.matrix('y')

    #load our data
    train_x = np.concatenate((
        np.array(np.ma.load("conv-white-chess-training-input.data")),
        np.array(np.ma.load("conv-more-white-chess-training-input.data"))))

    train_y = np.concatenate((
        np.squeeze(np.array(np.ma.load("white-chess-training-output.data"))),
        np.squeeze(np.array(np.ma.load("more-white-chess-training-output.data")))))

    # create the neural network
    #network = build_model(input_var, target_var)
    #input_var, network = build_model()

    # create loss function
    prediction = lasagne.layers.get_output(network)
    loss = lasagne.objectives.categorical_crossentropy(prediction, target_var)
    loss = loss.mean() + 1e-4
    """* lasagne.regularization.regularize_network_params(
            network, lasagne.regularization.l2)"""

    # create parameter update expressions
    params = lasagne.layers.get_all_params(network, trainable=True)
    """updates = lasagne.updates.nesterov_momentum(loss, params, learning_rate=0.01,
                                                momentum=0.9)"""

    learn = theano.shared(0.00005)

    updates = lasagne.updates.rmsprop(loss, params, learning_rate=learn)

    # compile training function that updates parameters and returns training loss
    train_fn = theano.function([input_var, target_var], loss, updates=updates)

    # train network (assuming you've got some training data in numpy arrays)
    batchsize = 6000
    for epoch in range(200):
        loss = 0
        batches = 0
        batchloss = 0
        for batch in iterate_minibatches(train_x, train_y, batchsize, shuffle=True):
        	#inputs, targets = batch
        	#targets = targets.reshape(-1,1)
            batchloss = train_fn(batch[0], batch[1])
            loss += batchloss
            batches += 1
            print batches
            print("Minibatch %d: Loss %g" % (batches, batchloss / batchsize))
        if epoch % 10 == 0:
            learn *= 0.5
        if epoch % 1 == 0:
            save_model(network)
        print("Epoch %d: Loss %g" % (epoch + 1, loss / (batchsize * batches)))

    return input_var, network

if __name__ == "__main__":
    print "LOADING MODEL"
    input_var, network = build_network_from_model('conv-model.npz')
    train(input_var, network)


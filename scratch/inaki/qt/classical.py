import numpy as np
import qt.random as random
from qt.qubit import Qubit


def heaviside(a):
    if isinstance(a, np.ndarray):
        return (a >= 0).astype(int)
    else:
        return int(a >= 0)


def theta(a):
    return a * heaviside(a)


def prepare(lambdas, qubit):
    """
    Alice prepares and sends two bits to Bob

    Parameters
    ---------
    lambdas : ndarray
        Shared randomness as two normalized vectors in a numpy 2-d array

    qubit: Qubit
        A uniformly sampled pure state qubit

    Returns
    -------
    dict
        A dictionary with the shared randomness ('lambdas'), the random qubit ('qubit')
        and the bits to be communicated to Bob ('bits')
    """

    x = qubit.bloch_vector()
    bits = heaviside(np.matmul(x, lambdas.T))
    return {
        "lambdas": lambdas,
        "qubit": qubit,
        "bits": bits
    }


def measure_pvm(lambdas, bits, measurement):
    """
    Bob receives two bits from Alice and performs a random PVM

    Parameters
    ---------
    lambdas : ndarray
        Shared randomness as two normalized vectors in a numpy 2-d array

    bits: ndarray
        Bits communicated by Alice in a numpy 1-d array

    measurement: PVM
        A uniformly sampled PVM

    Returns
    -------
    dict
        A dictionary with the random measurement ('measurement') and
        the probabilities for each measurement outcome ('probabilities')
    """
    # flip shared randomness
    flip = np.where(bits == 0, -1, 1).reshape(2, 1)
    lambdas = np.multiply(lambdas, flip)

    # generate classical random PVM as Bloch vectors
    y = np.array([Qubit(measurement.basis[0]).bloch_vector(),
                  Qubit(measurement.basis[1]).bloch_vector()])

    # select lambdas for each measurement
    a = np.abs(np.matmul(lambdas, y.T))
    lambdas = lambdas[np.argmax(a, axis=0), :]

    # compute probabilities
    thetas = theta(np.matmul(y, lambdas.T))

    # print('\nThetas=\n{}'.format(thetas))

    p = np.diag(thetas) / np.sum(thetas, axis=0)

    return {
        "measurement": measurement,
        "probabilities": p
    }


def prepare_and_measure(shots):

    # Alice prepares a random qubit
    qubit = random.qubit()

    # Bob prepares a random measurement
    measurement = random.pvm()

    experiment = {
        "qubit": qubit,
        "measurement": measurement,
        "probabilities": {
            "b1": [],
            "b2": []
        }
    }

    for i in range(shots):

        # Alice and Bob's shared randomness
        shared_randomness = np.array([random.bloch_vector(), random.bloch_vector()])

        # Alice prepares
        alice = prepare(shared_randomness, qubit)

        # Bob measures
        bob = measure_pvm(shared_randomness, alice['bits'], measurement)

        b1 = abs(bob['probabilities'][0])
        b2 = abs(bob['probabilities'][1])

        experiment['probabilities']['b1'].append(b1)
        experiment['probabilities']['b2'].append(b2)

    print('\nBorn\'s Rule Probabilities={}'.format(bob['measurement'].probability(alice['qubit'].rho())))
    return experiment

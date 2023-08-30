import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle as pl
import numpy as np

import numpy as np

def compute_mape(var, var_hat):
    return np.sum(np.abs(var - var_hat) / var) / var.shape[0]

def compute_rmse(var, var_hat):
    return np.sqrt(np.sum((var - var_hat) ** 2) / var.shape[0])

def laplacian(T, tau):
    ell = np.zeros(T)
    ell[0] = 2 * tau
    for k in range(tau):
        ell[k + 1] = -1
        ell[-k - 1] = -1
    return ell

def prox_2d(z, w, lmbda, denominator):
    N, T = z.shape
    temp = np.fft.fft2(lmbda * z - w) / denominator
    temp1 = 1 - N * T / (lmbda * np.abs(temp))
    temp1[temp1 <= 0] = 0
    return np.fft.ifft2(temp * temp1).real

def update_z(y_train, pos_train, x, w, lmbda, eta):
    z = x + w / lmbda
    z[pos_train] = (lmbda / (lmbda + eta) * z[pos_train]
                    + eta / (lmbda + eta) * y_train)
    return z

def update_w(x, z, w, lmbda):
    return w + lmbda * (x - z)

def LCR_2d(y_true, y, lmbda, gamma, tau_s, tau, maxiter = 50):
    eta = 100 * lmbda
    N, T = y.shape
    pos_train = np.where(y != 0)
    y_train = y[pos_train]
    pos_test = np.where((y_true != 0) & (y == 0))
    y_test = y_true[pos_test]
    z = y.copy()
    w = y.copy()
    ell_s = laplacian(N, tau_s)
    ell_t = laplacian(T, tau)
    denominator = lmbda + gamma * np.fft.fft2(np.outer(ell_s, ell_t)) ** 2
    del y_true, y
    show_iter = 20
    for it in range(maxiter):
        x = prox_2d(z, w, lmbda, denominator)
        z = update_z(y_train, pos_train, x, w, lmbda, eta)
        w = update_w(x, z, w, lmbda)
        if (it + 1) % show_iter == 0:
            print(it + 1)
            print(compute_mape(y_test, x[pos_test]))
            print(compute_rmse(y_test, x[pos_test]))
            print()
    return x
import numpy as np
np.random.seed(1000)
import scipy.io

dense_list=[]
tensorone = scipy.io.loadmat('tensor111.mat')
dense_one = tensorone['tensor']

# tensortwo = scipy.io.loadmat('tensor2.mat')
# dense_two = tensortwo['tensor']
dense_list.append(dense_one)
# dense_list.append(dense_two)
dense_tensor=np.array(dense_list)
dim =np.shape(dense_tensor)
missing_rate = 0.7

sparse_tensor = dense_tensor * np.round(np.random.rand(dim[0], dim[1])[:, :, np.newaxis] + 0.5 - missing_rate)

dense_mat = dense_tensor.reshape([dim[0]*dim[1] , dim[2]])
sparse_mat = sparse_tensor.reshape([dim[0]*dim[1] , dim[2]])
del dense_tensor, sparse_tensor
dense_mat = dense_mat[80:287,0:116 ] #取全部数据
sparse_mat = sparse_mat[80:287,0:116]

import time
start = time.time()
N, T = sparse_mat.shape
lmbda = 1e-5 * N * T
gamma = 1 * lmbda
tau_s = 1
tau = 5
maxiter = 150
mat_hat = LCR_2d(dense_mat, sparse_mat, lmbda, gamma, tau_s, tau, maxiter)
end = time.time()
print('Running time: %d seconds.'%(end - start))


fig = plt.figure(figsize = (12, 2.5))
sns.heatmap(mat_hat, cmap='jet_r', cbar_kws={'label': 'Traffic speed'}, vmin = 0, vmax = 75)
plt.xticks(np.arange(0, 117, 250), np.arange(0, 117, 250), rotation = 0)
plt.yticks(np.arange(0.5, 75.5, 10), np.arange(166, 241, 10), rotation = 0)
plt.xlabel('Time')
plt.ylabel('Loop detector')
plt.show()
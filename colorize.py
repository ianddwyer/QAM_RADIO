# -*- coding: utf-8 -*-
"""
Created on Sun Jun 29 01:38:08 2025

@author: Eian
"""



import torch
torch.cuda.is_available()
import torchvision
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
from torchvision import datasets, transforms
from matplotlib.pyplot import imshow, imsave
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

loss_perepoch = []

class ConvAE(nn.Module):
  def __init__(self):
    super(ConvAE, self).__init__()

    #Convolutional Encoder Layer structure based on:  http://richzhang.github.io/colorization/

    # note that there are 3 grayscale channels going into the AE, 3 color out
    # remember that stride 2 helps with image processing and removes need for pooling layer
    
    
    
    self.encoder = nn.Sequential(
                                                  # total size: divide by 2 for each due to stride and kernel size
        nn.Conv2d(3, 512, 4, stride=2, padding=1, bias=True), #  64*256*256 dimensions (channels, height, width)
        nn.BatchNorm2d(512),
        nn.ReLU(),
        
        nn.Conv2d(512, 512, 4, stride=2, padding=1, bias=True), # 512*32*32 dimensions (channels, height, width)
        nn.BatchNorm2d(512),
        nn.ReLU(),

    )

    
    self.decoder = nn.Sequential(
        
        nn.ConvTranspose2d(512, 512, 4, stride=2, padding=1, bias=True),
        nn.BatchNorm2d(512),
        nn.ReLU(),

        nn.ConvTranspose2d(512, 3, 4, stride=2, padding=1, bias=True),
        nn.BatchNorm2d(3),
    )

    self.out = nn.Sequential(nn.Sigmoid()) # output is a sigmoid activation to produce a logistic spread of img data
  
  def forward(self, x):
    """ ON ENDCODER """
    """ rescale from grayscale (possibly do this in transformations)"""
    """ differential encoding applied"""
    """ apply coding for FEC on drift? """
    """ map bits here for each 8-bit image (possibly do this in transformations)"""
    """ orthonormal transformation here (possibly do this in transformations)"""
    """ apply ofdm for 2d multi-access """
    
    """ ON DECODER """
    """ coherence corrections here """
    """ undo ofdm for 2d multi-access """
    """ use matched fileter to transform back to complex form """
    """ remap back to bytes for comparison """
    """ correct drift with FEC? """
    """ differential decoding applied """
    
    """ maybe add latent space recolorization """
    return self.out(self.decoder(self.encoder(x)))



def transform(train_dir,test_dir):
  train_trans = transforms.Compose([
                                  transforms.ToTensor(),
#using gaussian blur with large kernel to keep it from leaning lines (and face features) as much as color blurs to overlay. The residual part of the network should help with line weights and the encoder will just focus on color weights
#                                  transforms.RandomRotation(30),
#                                  transforms.RandomHorizontalFlip(),
#                                  transforms.GaussianBlur(kernel_size=7)
                                  ]) 

  test_trans = transforms.Compose([transforms.ToTensor()])  

  train_data = datasets.ImageFolder(train_dir, transform=train_trans)
  test_data = datasets.ImageFolder(test_dir, transform=test_trans)
  return train_data,test_data

def fit_model(train_loader, test_loader, network, optimizer, criterion):
  network.train()
  for epoch in range(epochs):

    print(datetime.now().strftime(f"Epoch {epoch} Start: %H:%M - %m/%d/%Y "))
    train_loss = 0
    test_loss = 0
    for data, label in train_loader:
      """ LOADING TO DEVICE TAKES WAY TOO LONG! CAN WE PRELOAD THIS? """
      #data, label = data.to(device), label.to(device) 
      """ Rescale chroma from grayscale using general form """
      #scalars = torch.tensor([1-0.299, 1-0.587, 1-0.114])[:, None, None].to(device) 
      logit = network(transforms.Grayscale(3)(data)) # grayscale input into network
      """ USE PCA COMPARISON HERE? """
      loss = criterion(logit, data) ## input gray training data and loss is against color training data. This should update the weights in favor of coloring the grayscale images
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()

      train_loss += loss.data
    
    scheduler.step()

    test_loss = 0
    network.eval()
    with torch.no_grad():
      for data, label in test_loader:
          #data = data.to(device)
          outputs = network(transforms.Grayscale(3)(data))
          loss = criterion(outputs, data) ## test loss needs to compare color and grayscale 
          test_loss += loss.data
    global loss_perepoch
    loss_perepoch = loss_perepoch.append(test_loss)

    #saves & prints intermitten images and values through training 
    if (epoch == 0) or ((epoch+1) % 1 == 0):
        print(f"\ntrain epoch: {epoch+1}\ntrain loss: {train_loss/len(train_loader)}")
        print(f"test loss: {test_loss/len(test_loader)}")
        plot_image_reconstruction(network, img_loader, 1, [0,epoch+1]) 
    
def plot_image_reconstruction(network, imgs, img_num, idx):

     network.eval()
     for batch in imgs:
        
        img, _ = batch
        img = img.to(device)
        gray = transforms.Grayscale(3)(img)
        output = network(gray)
        output = output.view(output.size(0), 3, 512, 512).cpu().data
        plt.figure()
        f, axarr = plt.subplots(1,3)
        axarr[0].imshow(img.permute(0, 2, 3, 1).cpu()[img_num])
        axarr[1].imshow(gray.permute(0, 2, 3, 1).cpu()[img_num])
        axarr[2].imshow(output.permute(0, 2, 3, 1)[img_num])
        if idx[0] == 0: plt.title(f'Epoch number {idx[1]}')
        if idx[0] == 1: plt.title(f'Image Number {idx[1]}')
        plt.show()
        break

train_dir = 'C:\\Users\\Eian\\Desktop\\all_desktop_01092025\\EE_References\\Summer_22\\Pytorch Class\\Lab4\\face-HQ\\train'
test_dir = 'C:\\Users\\Eian\\Desktop\\all_desktop_01092025\\EE_References\\Summer_22\\Pytorch Class\\Lab4\\face-HQ\\test'


## sample size 3000, train=2700, test=300
device = torch.device('cuda') ## not sure I need to use CPU at all but good to know ('cuda' if torch.cuda.is_available() else 'cpu')
torch.cuda.empty_cache()
## small batch size due to only 1 input, 1 output and 3000 samples
batch_size = 1
learning_rate = 0.0005 
epochs = 100 

print_imgs =  2 ##sets up the print with images from test_loader data set (reloaded as img_loader)

network = ConvAE().to(device)  
optimizer = optim.Adam(network.parameters(),lr=learning_rate)
criterion = nn.MSELoss().to(device)   ## using MSE due to image reconstruction be about finding regression, not classifying
# note: gamma is set to 0.5 to prevent too large of change in the learning rate
scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=np.linspace(20,100, 8), gamma=0.5)
train_data,test_data = transform(train_dir, test_dir)



""" """
train_data = torch.utils.data.Subset(train_data, indices=range(70))
test_data = torch.utils.data.Subset(test_data, indices=range(30))

# Preload entire dataset to CUDA (assuming GPU memory can hold it)
train_images = []
train_labels = []

test_images = []
test_labels = []


for img, label in train_data:
    train_images.append(img.to(device))
    train_labels.append(torch.tensor(label, device=device))
    
for img, label in test_data:
    test_images.append(img.to(device))
    test_labels.append(torch.tensor(label, device=device))

# Stack into tensors
Xtrain = torch.stack(train_images)
ytrain = torch.stack(train_labels)
Xtest = torch.stack(test_images)
ytest = torch.stack(test_labels)

# Optional: Create a TensorDataset and DataLoader
from torch.utils.data import TensorDataset

train_dataset = TensorDataset(Xtrain, ytrain)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

test_dataset = TensorDataset(Xtest, ytest)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)
""" """


# train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size,shuffle=True, pin_memory=True)
# test_loader = torch.utils.data.DataLoader(test_data, batch_size = batch_size)
img_loader = torch.utils.data.DataLoader(test_data, batch_size = print_imgs)


# network.load_state_dict(torch.load( 'drive/MyDrive/face-HQ/model_save/Colorize_ConvAE2'))

# torch.save(network.state_dict(), 'drive/MyDrive/face-HQ/model_save/Colorize_ConvAE2')


# note that the total photo limit is based on img_print size in 'settings'
#for ii in range(print_imgs): plot_image_reconstruction(network, img_loader, img_num=ii, idx=[1,ii+1])


print(f"PRINT SETTINGS\nBATCH SIZE: {batch_size} \nLR: {learning_rate} \nCRITERION: {criterion} \nOPTIMIZER: {optimizer} \nNETWORK: {network} ")
fit_model(train_loader, test_loader, network, optimizer, criterion)
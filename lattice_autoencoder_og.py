from keras.layers import Input, Dense, Reshape, Flatten, Dropout
from keras.layers import BatchNormalization, Activation, ZeroPadding2D
from keras.layers import LeakyReLU,ReLU
from keras.layers import UpSampling2D, Conv2D, Conv3DTranspose, Conv3D
from keras.models import Sequential, Model,load_model
from keras.optimizers import Adam
from keras import backend
from keras import regularizers
import tensorflow as tf
import numpy as np
import os
import random
import pandas as pd

def threshold(x):
 x = tf.clip_by_value(x,0.5,0.5001) - 0.5
 x = tf.minimum(x * 10000,1) 
 return x

def mkdir(path): #define a function to create non-existed folder automatically
 folder = os.path.exists(path)
 if not folder:
  os.makedirs(path)
  print("---  new folder...  ---")
  print("---  OK  ---")
 else:
  print("---  There is this folder!  ---")

def train_test_split(path, train_ratio, validation_ratio, test_ratio, whether_from_text=True, text_directory='../database/20201009version/2_3_properties_primitive_cell_selected_cL10_aN20.csv'):
    if whether_from_text == False:
        filename = os.listdir(path)
        name_list = [eachnpyfile[:-4] for eachnpyfile in filename if eachnpyfile.endswith('.npy')]
    else:
        df = pd.read_csv(text_directory)
        name_list = df['pretty_formula'].tolist()
    
    test_size = round(test_ratio * len(name_list))
    validation_size = round(validation_ratio * len(name_list))
    
    random.seed(1)
    random.shuffle(name_list)
    
    train_name_list = name_list[test_size + validation_size:]
    validation_name_list = name_list[test_size:test_size + validation_size]
    test_name_list = name_list[:test_size]
    
    return name_list, train_name_list, validation_name_list, test_name_list
'''
#This is the original train_test-split function
def train_test_split(path,train_ratio,validation_ratio,test_ratio,whether_from_text=True,text_directory='../database/20201009version/2_3_properties_primitive_cell_selected_cL10_aN20.txt'):
 if whether_from_text==False:
  filename=os.listdir(path)
  name_list=[]
  for eachnpyfile in filename:
   if eachnpyfile.endswith('.npy'):
    name_list.append(eachnpyfile[:-4])
 else:
  f=open(text_directory,'r')
  lines=f.readlines()
  f.close()
  lines=lines[1:]
  name_list=[]
  for line in lines:
   name_list.append(line.split()[0])
 test_size=round(test_ratio*len(name_list))
 validation_size=round(validation_ratio*len(name_list))
 random.seed(1)
 random.shuffle(name_list)
 train_name_list=name_list[test_size+validation_size:]
 validation_name_list=name_list[test_size:test_size+validation_size]
 test_name_list=name_list[:test_size]
 return name_list,train_name_list,validation_name_list,test_name_list

 '''

class lattice_autoencoder():
 def __init__(self,learning_rate):
  # Input shape
  self.a_axis = 32
  self.b_axis = 32
  self.c_axis = 32
  self.channels = 1
  self.voxel_shape = (self.a_axis, self.b_axis, self.c_axis, self.channels)
  self.latent_dim = 25
  self.img_shape = (1, 1, 1, self.latent_dim)
  self.learning_rate= learning_rate
  optimizer = Adam(self.learning_rate)#0.0002,0.5

  # Build the encoder
  self.encoder = self.build_encoder()
  # Build the decoder
  self.decoder = self.build_decoder()
  # The encoder takes voxels as input and generates encodeds
  inupt_voxels = Input(shape=self.voxel_shape)
  encodeds = self.encoder(inupt_voxels)
  # The decoder takes generated encodeds as input and determines voxels
  output_voxels = self.decoder(encodeds)
  # The combined model  (stacked encoder and decoder)
  # Trains them
  self.combined = Model(inupt_voxels, output_voxels)
  self.combined.compile(loss='mse', optimizer=optimizer)

 def build_encoder(self):
    # Define the input for the encoder
    input_voxel = Input(shape=self.voxel_shape)

    # First Conv3D layer
    x = Conv3D(128, kernel_size=4, strides=2, padding="same")(input_voxel)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    # Combined Conv3D layer (originally two separate layers)
    x = Conv3D(512, kernel_size=4, strides=2, padding="same")(x)  # Merged two layers
    x = BatchNormalization()(x)
    x = ReLU()(x)

    # Flatten the output and add a dense layer for encoding
    x = Flatten()(x) 
    encoded = Dense(self.latent_dim)(x)  # Output to latent space

    # Create the encoder model
    return Model(inputs=input_voxel, outputs=encoded)
 
 def build_decoder(self):
    # Define the input for the decoder
    input_latent = Input(shape=(self.latent_dim,))

    # Dense layer and reshape
    x = Dense(512 * 4 * 4 * 4)(input_latent)
    x = ReLU()(x)
    x = Reshape((4, 4, 4, 512))(x)

    # First Conv3DTranspose layer
    x = Conv3DTranspose(256, kernel_size=4, strides=2, padding="same")(x)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    # Second Conv3DTranspose layer
    x = Conv3DTranspose(128, kernel_size=4, strides=2, padding="same")(x)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    # Output layer with Conv3DTranspose
    output_voxel = Conv3DTranspose(1, kernel_size=4, strides=2, padding="same")(x)
    output_voxel = Activation("tanh")(output_voxel)

    # Create the decoder model
    return Model(inputs=input_latent, outputs=output_voxel)




 
 '''
 #4800 or 5thousand low 1510 high
 def build_encoder(self):
    # Define the input for the encoder
    input_voxel = Input(shape=self.voxel_shape)

    # First Conv3D layer
    x = Conv3D(128, kernel_size=4, strides=2, padding="same")(input_voxel)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    # Second Conv3D layer
    x = Conv3D(256, kernel_size=4, strides=2, padding="same")(x)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    # Third Conv3D layer
    x = Conv3D(512, kernel_size=4, strides=2, padding="same")(x)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    # Flatten the output and add a dense layer for encoding
    x = Flatten()(x) 
    encoded = Dense(self.latent_dim)(x) #back to (25,)
  

    # Create the encoder model
    return Model(inputs=input_voxel, outputs=encoded)

 def build_decoder(self):
    # Define the input for the decoder
    input_latent = Input(shape=(self.latent_dim,))

    # Dense layer and reshape
    x = Dense(512 * 4 * 4 * 4)(input_latent)
    x = ReLU()(x)
    x = Reshape((4, 4, 4, 512))(x)

    # First Conv3DTranspose layer
    x = Conv3DTranspose(256, kernel_size=4, strides=2, padding="same")(x)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    # Second Conv3DTranspose layer
    x = Conv3DTranspose(128, kernel_size=4, strides=2, padding="same")(x)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    # Output layer with Conv3DTranspose
    output_voxel = Conv3DTranspose(1, kernel_size=4, strides=2, padding="same")(x)
    output_voxel = Activation("tanh")(output_voxel)

    # Create the decoder model
    return Model(inputs=input_latent, outputs=output_voxel)


 
 #4399 bad reproductions  low 
 def build_encoder(self):
    model = Sequential()

    model.add(Conv3D(128, kernel_size=4, strides=2, input_shape=self.voxel_shape, padding="same"))
    model.add(BatchNormalization())
    model.add(ReLU())
    model.add(Dropout(0.3))  # Add Dropout

    model.add(Conv3D(256, kernel_size=4, strides=2, padding="same"))
    model.add(BatchNormalization())
    model.add(ReLU())
    model.add(Dropout(0.3))  # Add Dropout

    model.add(Conv3D(512, kernel_size=4, strides=2, padding="same"))
    model.add(BatchNormalization())
    model.add(ReLU())
    model.add(Dropout(0.3))  # Add Dropout

    model.add(Flatten())
    model.add(Dense(self.latent_dim, kernel_regularizer='l2'))  # L2 Regularization
    model.add(Activation("tanh"))

    model.summary()

    voxel = Input(shape=self.voxel_shape)
    encoded = model(voxel)

    return Model(voxel, encoded)

 def build_decoder(self):
    model = Sequential()

    model.add(Dense(512 * 4 * 4 * 4, input_shape=(self.latent_dim,)))
    model.add(ReLU())
    model.add(Reshape((4, 4, 4, 512)))

    model.add(Conv3DTranspose(256, kernel_size=4, strides=2, padding="same"))
    model.add(BatchNormalization())
    model.add(ReLU())
    model.add(Dropout(0.3))  # Add Dropout

    model.add(Conv3DTranspose(128, kernel_size=4, strides=2, padding="same"))
    model.add(BatchNormalization())
    model.add(ReLU())
    model.add(Dropout(0.3))  # Add Dropout

    model.add(Conv3DTranspose(1, kernel_size=4, strides=2, padding="same"))
    model.add(Activation("tanh"))

    model.summary()

    encoded = Input((self.latent_dim,))
    voxel = model(encoded)

    return Model(encoded, voxel)

 #4995 high complexity
 def build_encoder(self):
    model = Sequential()

    # First Conv3D layer with slightly more filters
    model.add(Conv3D(96, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(1e-6), input_shape=self.voxel_shape, padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.2))

    # Second Conv3D layer with increased filters
    model.add(Conv3D(96, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(1e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.2))

    # Third Conv3D layer with additional filters
    model.add(Conv3D(128, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(1e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.2))

    # Fourth Conv3D layer for extra depth
    model.add(Conv3D(256, kernel_size=4, strides=1, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(1e-6), padding="valid"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())

    # Flatten output
    model.add(Flatten())

    # Dense layers
    model.add(Dense(256))
    model.add(ReLU())

    model.add(Dense(256))
    model.add(ReLU())
    
    # Output layer for the latent space
    model.add(Dense(self.latent_dim))
    model.add(Activation("tanh"))

    model.summary()

    voxel = Input(shape=self.voxel_shape)
    encoded = model(voxel)

    return Model(voxel, encoded)
 
 def build_decoder(self):
    model = Sequential()

    # First Dense layer with 256 neurons (adjusted to match reshape target)
    model.add(Dense(256, input_shape=(self.latent_dim,)))
    model.add(ReLU())

    # Second Dense layer
    model.add(Dense(512))
    model.add(ReLU())

    # Adjusted Reshape to match the 256 neurons in the previous Dense layer
    model.add(Reshape((1, 1, 1, 256)))

    # Remaining layers (unchanged)
    model.add(Conv3DTranspose(128, kernel_size=4, strides=1, padding="valid"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Conv3DTranspose(128, kernel_size=4, strides=2, padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Conv3DTranspose(64, kernel_size=4, strides=2, padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Conv3DTranspose(1, kernel_size=4, strides=2, padding="same"))
    model.add(Activation("tanh"))

    model.summary()

    encoded = Input((self.latent_dim,))
    voxel = model(encoded)

    return Model(encoded, voxel)


 
 def build_encoder(self):
    model = Sequential()

    # Reduce the number of filters
    model.add(Conv3D(32, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), input_shape=self.voxel_shape, padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    #model.add(Dropout(0.1))

    model.add(Conv3D(32, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    #model.add(Dropout(0.1))

    model.add(Conv3D(64, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    #model.add(Dropout(0.1))

    # Keep the number of dense layers minimal
    model.add(Flatten())
    model.add(Dense(128))  # Reduced size of dense layer
    model.add(ReLU())
    
    model.add(Dense(self.latent_dim))
    model.add(Activation("tanh"))

    model.summary()

    voxel = Input(shape=self.voxel_shape)
    encoded = model(voxel)

    return Model(voxel, encoded)

 def build_decoder(self):
    model = Sequential()

    # Simplify the fully connected layers
    model.add(Dense(128, input_shape=(self.latent_dim,)))
    model.add(ReLU())

    model.add(Dense(128))
    model.add(ReLU())
    
    model.add(Reshape((1, 1, 1, 128)))  # Reduced reshape size

    # Reduce the number of filters and keep the architecture shallower
    model.add(Conv3DTranspose(64, kernel_size=4, strides=1, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="valid"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    #model.add(Dropout(0.1))

    model.add(Conv3DTranspose(32, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
   # model.add(Dropout(0.1))

    model.add(Conv3DTranspose(32, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
   # model.add(Dropout(0.1))

    model.add(Conv3DTranspose(1, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(Activation("tanh"))

    model.summary()

    encoded = Input((self.latent_dim,))
    voxel = model(encoded)

    return Model(encoded, voxel)

 
 def build_encoder(self):
    model = Sequential()

    # Add more convolutional layers with increasing filters
    model.add(Conv3D(64, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), input_shape=self.voxel_shape, padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))  # Slightly increase dropout to prevent overfitting

    model.add(Conv3D(128, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Conv3D(256, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))

    # Add one more layer to increase complexity
    model.add(Conv3D(512, kernel_size=4, strides=1, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="valid"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Flatten())

    # Increased fully connected layers for more complexity
    model.add(Dense(512))
    model.add(ReLU())
    model.add(Dropout(0.3))  # Add dropout to dense layers

    model.add(Dense(256))
    model.add(ReLU())
    
    model.add(Dense(self.latent_dim))
    model.add(Activation("tanh"))

    model.summary()

    voxel = Input(shape=self.voxel_shape)
    encoded = model(voxel)

    return Model(voxel, encoded)

 def build_decoder(self):
    model = Sequential()

    # Add deeper fully connected layers
    model.add(Dense(512, input_shape=(self.latent_dim,)))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Dense(512))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Dense(256))
    model.add(ReLU())
    
    model.add(Reshape((1, 1, 1, 256)))

    # Add more layers and filters, keep strides same to maintain dimensionality
    model.add(Conv3DTranspose(256, kernel_size=4, strides=1, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="valid"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Conv3DTranspose(128, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Conv3DTranspose(64, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(ReLU())
    model.add(Dropout(0.3))

    model.add(Conv3DTranspose(1, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
    model.add(BatchNormalization(momentum=0.9))
    model.add(Activation("tanh"))
    model.add(Dropout(0.3))

    model.summary()

    encoded = Input((self.latent_dim,))
    voxel = model(encoded)

    return Model(encoded, voxel)

 
 def build_encoder(self):
  model = Sequential()

  model.add(Conv3D(64, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), input_shape=self.voxel_shape, padding="same"))
  model.add(BatchNormalization(momentum=0.9))
  model.add(ReLU())
  model.add(Dropout(0.2))

  model.add(Conv3D(64, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
  model.add(BatchNormalization(momentum=0.9))
  model.add(ReLU())
  model.add(Dropout(0.2))

  model.add(Conv3D(64, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
  model.add(BatchNormalization(momentum=0.9))
  model.add(ReLU())
  model.add(Dropout(0.2))

  model.add(Conv3D(256, kernel_size=4, strides=1, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="valid"))
  model.add(BatchNormalization(momentum=0.9))
  model.add(ReLU())
  

  model.add(Flatten())


  model.add(Dense(256))
  model.add(ReLU())

  model.add(Dense(256))
  model.add(ReLU())
  
  model.add(Dense(self.latent_dim))
  model.add(Activation("tanh"))

  model.summary()

  voxel = Input(shape=self.voxel_shape)
  encoded = model(voxel)

  return Model(voxel, encoded)

 def build_decoder(self):

  model = Sequential()
  
  model.add(Dense(256,input_shape=(self.latent_dim,)))
  model.add(ReLU())
  
  model.add(Dense(256))
  model.add(ReLU())

  model.add(Dense(256))
  model.add(ReLU())
  
  model.add(Reshape((1,1,1,256)))
  
  model.add(Conv3DTranspose(64, kernel_size=4, strides=1, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="valid"))
  model.add(BatchNormalization(momentum=0.9))
  model.add(ReLU())
  model.add(Dropout(0.2))
  
  model.add(Conv3DTranspose(64, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
  model.add(BatchNormalization(momentum=0.9))
  model.add(ReLU())
  model.add(Dropout(0.2))
  
  model.add(Conv3DTranspose(64, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
  model.add(BatchNormalization(momentum=0.9))
  model.add(ReLU())
  model.add(Dropout(0.2))

  model.add(Conv3DTranspose(1, kernel_size=4, strides=2, kernel_initializer="glorot_normal", kernel_regularizer=regularizers.l2(0.0e-6), padding="same"))
  model.add(BatchNormalization(momentum=0.9))
  model.add(Activation("tanh"))
  model.add(Dropout(0.2))
  
  model.add(Activation('relu'))
  
  model.summary()

  encoded = Input((self.latent_dim,))
  voxel = model(encoded)

  return Model(encoded, voxel)

  '''
 
 #@tf.function(experimental_relax_shapes=True)
 def train(self, epochs, batch_size, train_name_list,validation_name_list,test_name_list, lattice_voxel_path, model_folder_path):

  # Recored the training loss
  mkdir(model_folder_path)
  g=open(model_folder_path+'lattice_autoencoder_learning_curve_new.txt','w')
  g.write('epoch train_loss validation_loss')
  g.write('\n')
  best_loss=100

  print('inside TRAIN')
  print('Total batch size : ',batch_size)
  print('Total epochs : ',epochs)
  count1,count2 = 0,0
  for epoch in range(epochs):
    
    count1 += 1
    print('Epoch Count:', count1)

    np.random.seed(epoch)
    idx = np.random.randint(0, len(train_name_list), batch_size)
    
    # Train the model
    train_loss = 0
    for i in range(batch_size):
        count2 += 1
        print('Batch Count:', count2)
        
        # Check if file exists
        file_path = lattice_voxel_path + train_name_list[idx[i]] + '.npy'
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}, skipping this batch.")
            continue
        
        inputs_batch = np.load(file_path).reshape(1, 32, 32, 32, 1)
        train_loss += self.combined.train_on_batch(inputs_batch, inputs_batch)
    
    train_loss = train_loss / batch_size
      
    # Test the model
    validation_loss = 0
    for i in range(len(validation_name_list)):
        file_path = lattice_voxel_path + validation_name_list[i] + '.npy'
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}, skipping this validation sample.")
            continue
        
        inputs_batch = np.load(file_path).reshape(1, 32, 32, 32, 1)
        validation_loss += self.combined.test_on_batch(inputs_batch, inputs_batch)
    
    validation_loss = validation_loss / len(validation_name_list)
      
    # Plot the progress
    print(f"Epoch: {epoch} [Train loss: {train_loss}] [Validation loss: {validation_loss}]")
    new_line = f"{epoch} {train_loss} {validation_loss}\n"
    g.write(new_line)
      
    # Save the best model if the validation loss improves
    if validation_loss < best_loss:
        best_loss = validation_loss
        encoder_path = model_folder_path + 'lattice_encoder_new.keras'
        decoder_path = model_folder_path + 'lattice_decoder_new.keras'
        
        # Check if the models already exist, replace if better
        if os.path.exists(encoder_path) and os.path.exists(decoder_path):
            print("Better model found, replacing existing model.")
        else:
            print("Saving new best model.")
            
        self.encoder.save(encoder_path)
        self.decoder.save(decoder_path)

  # Test the model
  test_loss = 0
  for i in range(len(test_name_list)):
      file_path = lattice_voxel_path + test_name_list[i] + '.npy'
      if not os.path.exists(file_path):
          print(f"File not found: {file_path}, skipping this test sample.")
          continue
      
      inputs_batch = np.load(file_path).reshape(1, 32, 32, 32, 1)
      test_loss += self.combined.test_on_batch(inputs_batch, inputs_batch)
  test_loss = test_loss / len(test_name_list)

  # Write final results
  g.write(f'\nLearning rate: {self.learning_rate}')
  g.write('\nBatch normalization momentum: 0.9')
  g.write(f'\nBest validation loss: {best_loss}')
  g.write(f'\nTest loss: {test_loss}')
  g.close()

  return best_loss, test_loss

 def rebuild_decoder(self,previous_model_path):
  model = load_model(previous_model_path+'lattice_decoder_new.keras')
  model.summary()
  return model

 def rebuild_encoder(self,previous_model_path):
  model = load_model(previous_model_path+'lattice_encoder_new.keras')
  model.summary()
  return model

 def generate_encoded(self,lattice_voxel):
  encoded_lattice = np.zeros((200,1))
  encoded_lattice[:self.latent_dim,:] = self.encoder.predict(lattice_voxel).reshape(self.latent_dim,1)       
  return encoded_lattice
        
 def generate_voxel(self,encoded_lattice):
  lattice_voxel = self.decoder.predict(encoded_lattice.reshape(1,self.latent_dim)).reshape(32,32,32)  
  #lattice_voxel = self.decoder.predict(encoded_lattice[:25,:].reshape(1, self.latent_dim)).reshape(32, 32, 32)
  #lattice_voxel = self.decoder.predict(encoded_lattice.reshape(1,1,1,1,self.latent_dim)).reshape(32,32,32)       

     
  return lattice_voxel

class find_best_autoencoder(): #epochs original 200 and batch size was 8
 def __init__(self, lattice_voxel_path='./', model_folder_path='./', encoded_lattice_path='./', epochs=20, batch_size=1000,train_ratio=0.8,validation_ratio=0.1,test_ratio=0.1,whether_training=True,whether_learning_rate_tune=True,learning_rate=0.0003,whether_encoded_generate=True,whether_from_text=True,text_directory='D:/April Progress (CREEP)/cleaned_data.csv'):
  # Load the dataset
  print('INSIDE FIND BEST AUTOENCODER')
  name_list,train_name_list,validation_name_list,test_name_list = train_test_split(lattice_voxel_path,train_ratio,validation_ratio,test_ratio,whether_from_text,text_directory)
  print('executed till here')
  if whether_training==True:
   if whether_learning_rate_tune==True:
    # Compare to get the best model
    best_loss=100
    learning_rate_list=[0.001,0.0003,0.0001,0.00003,0.00001]
    for i in range(5):
     if i<5:
      print('inside if 1')
      ae=lattice_autoencoder(learning_rate_list[i])
      validation_loss, test_loss=ae.train(epochs, batch_size, train_name_list,validation_name_list,test_name_list, lattice_voxel_path, model_folder_path+'lr_'+str(learning_rate_list[i])+'/')
      if validation_loss<best_loss:
       best_loss=validation_loss
       best_lr=learning_rate_list[i]
    command='cp '+model_folder_path+'lr_'+str(best_lr)+'/*.h5 '+model_folder_path
    os.system(command)
    command='cp '+model_folder_path+'lr_'+str(best_lr)+'/lattice_autoencoder_learning_curve_new.txt '+model_folder_path
    os.system(command)
   else:
    print('inside else')
    ae=lattice_autoencoder(learning_rate)
    validation_loss, test_loss=ae.train(epochs, batch_size, train_name_list,validation_name_list,test_name_list, lattice_voxel_path, model_folder_path)
   
  #Generate encoded lattice
  if whether_encoded_generate==True:
   ae=lattice_autoencoder(learning_rate)
   ae.rebuild_encoder(model_folder_path)
   mkdir(encoded_lattice_path)
   print('i made it till here but folder sould be created')
   for i in range(len(name_list)):
    inputs_batch=np.load(lattice_voxel_path+name_list[i]+'.npy').reshape(1,32,32,32,1)
    encoded_lattice=ae.generate_encoded(inputs_batch)
    np.save(encoded_lattice_path+name_list[i]+'.npy',encoded_lattice)

def restore_lattice_voxel_from_encoded_lattice(encoded_lattice_path,model_folder_path,lattice_voxel_path):
 ae=lattice_autoencoder(learning_rate=0.001)
 ae.rebuild_decoder(model_folder_path)
 mkdir(lattice_voxel_path)
 name_list=os.listdir(encoded_lattice_path)
 for i in range(len(name_list)):
  inputs_batch=np.load(encoded_lattice_path+name_list[i]).reshape(1,200)[:,:25] #CHANGED
  lattice_voxel=ae.generate_voxel(inputs_batch)
  np.save(lattice_voxel_path+name_list[i],lattice_voxel)

#find_best_autoencoder(lattice_voxel_path='./temp/original_lattice_voxel/', model_folder_path='./autoencoder_model/lattice/', encoded_lattice_path='./temp/original_encoded_lattice/', epochs=400, batch_size=1024, train_ratio=0.95,validation_ratio=0.025,test_ratio=0.025,whether_training=True,whether_learning_rate_tune=True,learning_rate=0.0001,whether_encoded_generate=True,whether_from_text=True,text_directory='../database/20201009version/other_properties_primitive_cell_selected_cL10_aN20.txt')

#restore_lattice_voxel_from_encoded_lattice(encoded_lattice_path='./temp/original_encoded_lattice/',model_folder_path='./autoencoder_model/lattice/',lattice_voxel_path='./temp/original_lattice_voxel_restored_from_autoencoder/')

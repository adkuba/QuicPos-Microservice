import tensorflow as tf
import numpy
import os

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

#spam detector net


#inputs
textInput = tf.keras.Input(shape=(200,))
imageInput = tf.keras.Input(shape=(1280,))

inputArray = [textInput, imageInput]


#additional dense
textDense = tf.keras.layers.Dense(256, activation='softmax', name="textDense")(textInput)
imageDense = tf.keras.layers.Dense(256, activation='softmax', name="imageDense")(imageInput)


#concat all + final layers
allCon = tf.keras.layers.Concatenate(name="allCon")([textDense, imageDense])
connected = tf.keras.layers.Dense(256, activation='softmax', name="connected")(allCon)
out = tf.keras.layers.Dense(1, activation='sigmoid', name="out")(connected)

#model
model = tf.keras.Model(inputs=inputArray, outputs=out)
print(model.summary())

#compile
model.compile(optimizer="adam", loss='binary_crossentropy', metrics=['accuracy'])


#test running
text = numpy.array([[0]*200])
image = numpy.array([[0]*1280])

myRandomInput = [text, image]

result = model.predict(myRandomInput)
print(result.tolist())

#save
model.save("./out/detector_new_init.h5")
tf.saved_model.save(model, "./out/detector_new")
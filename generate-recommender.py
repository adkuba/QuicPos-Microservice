import tensorflow as tf
import numpy
import os

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

#recommender net

#inputs
textInput = tf.keras.Input(shape=(200,))
imageInput = tf.keras.Input(shape=(1280,))
userInput = tf.keras.Input(shape=(4,))
viewsInput = tf.keras.Input(shape=(1,))
sharesInput = tf.keras.Input(shape=(1,))

inputArray = [textInput, imageInput, userInput, viewsInput, sharesInput]


#additional dense
textDense = tf.keras.layers.Dense(256, activation='softmax')(textInput)
imageDense = tf.keras.layers.Dense(256, activation='softmax')(imageInput)
userDense = tf.keras.layers.Dense(256, activation='softmax')(userInput)

#concat rest
numbersCon = tf.keras.layers.Concatenate()([viewsInput, sharesInput])
numbersDense = tf.keras.layers.Dense(256, activation='softmax')(numbersCon)

#concat all + final layers
allCon = tf.keras.layers.Concatenate()([textDense, imageDense, userDense, numbersDense])
connected = tf.keras.layers.Dense(256, activation='softmax')(allCon)
out = tf.keras.layers.Dense(1, activation='sigmoid', name="out")(connected)

#model
model = tf.keras.Model(inputs=inputArray, outputs=out)
print(model.summary())

#compile
model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])


#test running
text = numpy.array([[0]*200])
image = numpy.array([[0]*1280])
user = numpy.array([[0]*4])
views = numpy.array([0])
shares = numpy.array([0])

myRandomInput = [text, image, user, views, shares]

result = model.predict(myRandomInput)
print(result.tolist())

#save
model.save("./out/recommender_init.h5")
tf.saved_model.save(model, "./out/recommender")
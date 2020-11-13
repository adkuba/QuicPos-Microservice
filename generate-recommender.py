import tensorflow as tf
import numpy
import os

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

#recommender net

#inputs
textInput = tf.keras.Input(shape=(400,))
userInput = tf.keras.Input(shape=(1,))
reportsInput = tf.keras.Input(shape=(100,))
creationInput = tf.keras.Input(shape=(1,))
imageInput = tf.keras.Input(shape=(224, 224, 3))
viewsInput = tf.keras.Input(shape=(100, 6))
sharesInput = tf.keras.Input(shape=(100,))
requestingUserInput = tf.keras.Input(shape=(1,))
requestingLatInput = tf.keras.Input(shape=(1,))
requestingLongInput = tf.keras.Input(shape=(1,))
requestingTimeInput = tf.keras.Input(shape=(1,))

inputArray = [textInput, userInput, reportsInput, creationInput, imageInput, viewsInput, sharesInput, requestingUserInput, requestingLatInput, requestingLongInput, requestingTimeInput]


#additional dense
textDense = tf.keras.layers.Dense(128, activation='softmax')(textInput)
reportsDense = tf.keras.layers.Dense(128, activation='softmax')(reportsInput)
viewsFlat = tf.keras.layers.Flatten()(viewsInput)
viewsDense = tf.keras.layers.Dense(128, activation='softmax')(viewsFlat)
sharesDense = tf.keras.layers.Dense(128, activation='softmax')(sharesInput)

#image
conv1 = tf.keras.layers.Conv2D(2, 3, activation='softmax', input_shape=(224, 224, 3))(imageInput)
conv2 = tf.keras.layers.Conv2D(2, 3, activation='softmax', input_shape=conv1.shape)(conv1)
imageFlat = tf.keras.layers.Flatten()(conv2)
imageDense = tf.keras.layers.Dense(128, activation='softmax')(imageFlat)

#concat rest
restCon = tf.keras.layers.Concatenate()([userInput, creationInput, requestingUserInput, requestingLatInput, requestingLongInput, requestingTimeInput])
restDense = tf.keras.layers.Dense(128, activation='softmax')(restCon)

#concat all + final layers
allCon = tf.keras.layers.Concatenate()([textDense, reportsDense, viewsDense, sharesDense, imageDense, reportsDense])
connected = tf.keras.layers.Dense(256, activation='softmax')(allCon)
out = tf.keras.layers.Dense(5, activation='softmax')(connected)

#model
model = tf.keras.Model(inputs=inputArray, outputs=out)
#print(model.summary())

#compile
model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])


#test running
text = numpy.array([[0]*400])
user = numpy.array([[22344]])
reports = numpy.array([[0]*100])
creation = numpy.array([[2.3]])
image = numpy.array([[[ [0.1]*3 ]*224 ]*224])
views = numpy.array([[ [0]*6 ]*100])
shares = numpy.array([[0]*100])
requestingUser = numpy.array([[334]])
requestingLat = numpy.array([[51.23]])
requestingLong = numpy.array([[41.23]])
requestingTime = numpy.array([[227364]])

myRandomInput = [text, user, reports, creation, image, views, shares, requestingUser, requestingLat, requestingLong, requestingTime]

result = model.predict(myRandomInput)
print(result.tolist())

#save
model.save("./out/recommender.h5")
tf.saved_model.save(model, "./out/recommender")
import pickle
import matplotlib.pyplot as plt

path = "./training/"
names =[ 'recommender_history']
val_acc = []

for name in names:
    pickle_in = open(path + name, 'rb')
    history = pickle.load(pickle_in)
    val_acc += history['val_accuracy']

plt.plot(val_acc, label='recommender')
plt.xticks(range(0,len(val_acc)))
plt.legend(loc='upper left')
plt.ylabel('Accuracy')
plt.ylim([min(plt.ylim()),1])
plt.title('Validation Accuracy')
plt.show()
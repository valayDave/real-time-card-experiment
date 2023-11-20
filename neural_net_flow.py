from metaflow import FlowSpec, step, card, current, Parameter, pypi_base
from metaflow.cards import Image


def plot_learning_curves(history):
    import matplotlib.pyplot as plt

    fig1, ax = plt.subplots(1, 1)
    ax.plot(history.history["accuracy"])
    ax.plot(history.history["val_accuracy"])
    ax.set_title("model accuracy")
    ax.set_ylabel("accuracy")
    ax.set_xlabel("epoch")
    fig1.legend(["train", "test"], loc="upper left")
    fig2, ax = plt.subplots(1, 1)
    ax.plot(history.history["loss"])
    ax.plot(history.history["val_loss"])
    ax.set_title("model loss")
    ax.set_ylabel("loss")
    ax.set_xlabel("epoch")
    fig2.legend(["train", "test"], loc="upper left")
    return fig1, fig2


def get_model(num_classes):
    from tensorflow import keras  # pylint: disable=import-error
    from keras import layers, Sequential, Input  # pylint: disable=import-error

    return Sequential(
        [
            Input(shape=(28, 28, 1)),
            layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )


@pypi_base(python="3.11", packages={"tensorflow": "2.15.0"})
class NeuralNetCardFlow(FlowSpec):
    epochs = Parameter("epochs", default=10)

    batch_size = Parameter("batch-size", default=20)

    @step
    def start(self):
        import numpy as np
        from tensorflow import keras
        from keras import datasets, utils

        self.num_classes = 10
        ((x_train, y_train), (x_test, y_test)) = datasets.mnist.load_data()
        x_train = x_train.astype("float32") / 255
        x_test = x_test.astype("float32") / 255
        self.x_train = np.expand_dims(x_train, -1)
        self.x_test = np.expand_dims(x_test, -1)
        self.y_train = utils.to_categorical(y_train, self.num_classes)
        self.y_test = utils.to_categorical(y_test, self.num_classes)
        self.next(self.train_model)

    @card(type="blank")
    @step
    def train_model(self):
        from nn_card import MetaflowCardUpdates

        self.model = get_model(self.num_classes)
        self.model.compile(
            loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
        )
        history = self.model.fit(
            self.x_train,
            self.y_train,
            batch_size=self.batch_size,
            epochs=self.epochs,
            validation_split=0.1,
            callbacks=[
                MetaflowCardUpdates(log_every_n_steps=100)
            ],
        )
        
        # fig_acc, fig_loss = plot_learning_curves(history)
        # current.card.append(Image.from_matplotlib(fig_acc))
        # current.card.append(Image.from_matplotlib(fig_loss))
        self.next(self.end)

    @step
    def end(self):
        print("NeuralNetFlow is all done.")


if __name__ == "__main__":
    NeuralNetCardFlow()

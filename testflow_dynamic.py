from metaflow import FlowSpec, step, dynamic_card

class HelloFlow(FlowSpec):

    @dynamic_card(id="one")
    @dynamic_card
    @step
    def start(self):
        self.next(self.a)

    @dynamic_card(id="two")
    @dynamic_card(id="three")
    @dynamic_card
    @step
    def a(self):
        self.next(self.end)

    @dynamic_card
    @step
    def end(self):
        pass

if __name__ == '__main__':
    HelloFlow()
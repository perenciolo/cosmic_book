class FakeSession:
    committed: bool = False

    def commit(self):
        self.committed = True

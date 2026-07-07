import threading
import time
import random


class Regeneration:

    def __init__(self, simulator):
        self.simulator = simulator

    def start(self):

        if self.simulator.regeneration:
            print("Regeneration already running.")
            return False

        thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        thread.start()

        return True

    def run(self):

        print("===================================")
        print("Regeneration Started")
        print("===================================")

        self.simulator.regeneration = True
        self.simulator.regeneration_failed = False

        try:

            self.simulator.add_log("♻ Regeneration Started")

            success = random.random() < 0.8

            for i in range(10):

                print(f"Regenerating... {i+1}/10")

                time.sleep(1)

            if success:

                print("Regeneration Successful")

                self.simulator.tds = 120

                self.simulator.salt = max(
                    20,
                    self.simulator.salt - 2
                )

                self.simulator.regeneration_failed = False

                self.simulator.add_log(
                    "✅ Regeneration Completed Successfully"
                )

            else:

                print("Regeneration Failed")

                self.simulator.regeneration_failed = True

                self.simulator.add_log(
                    "❌ Regeneration Timeout"
                )

        except Exception as e:

            print("Regeneration Exception:", e)

            self.simulator.regeneration_failed = True

            try:
                self.simulator.add_log(
                    f"❌ Regeneration Error: {e}"
                )
            except Exception:
                pass

        finally:

            print("Resetting regeneration flag...")

            self.simulator.regeneration = False

            print("regeneration =", self.simulator.regeneration)

            print("===================================")
            print("Regeneration Thread Finished")
            print("===================================")
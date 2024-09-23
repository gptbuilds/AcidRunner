from acidrunner.acid_runner import AcidRunner

def load_runner(config_file: str | None):
    if config_file:
        try:
            runner = AcidRunner(config_file)
            config = runner.load_settings()

            return runner
        except Exception as e:
            print(f"Couldn't open {config_file}")
            raise Exception(f"Couldn't open {config_file}")
    else:
        try:
            runner = AcidRunner("Acidfile.yaml")
            config = runner.load_settings()

            return runner
        except Exception as e:
            print("Couldn't open Acidfile.yaml try and specify one with -f")
            raise Exception(f"Couldn't open {config_file}")

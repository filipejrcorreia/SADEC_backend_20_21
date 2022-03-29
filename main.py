from knowledge_management.knowledge_manager import Knowledge_Manager
from knowledge_management.data_manager import Data_Manager
from model_management.model_manager import Model_Manager
from entrypoints.entrypoints import run
import entrypoints.entrypoints as entrypoint
import argparse


if __name__ == "__main__":

    dm = Data_Manager()
    dm.update_data()
    mm = Model_Manager(dm)
    mm.set_dataframe(dm.get_patients_data())
    mm.train_model()
    km = Knowledge_Manager(mm,dm)

    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(km,addr=args.listen, port=args.port)
from dotenv import load_dotenv
import sys, os

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH"))

available_models = ["RNN"]


def create_model(config):

    model_type = config["architecture"]["type"]

    if model_type in available_models:

        if model_type == "RNN":

            from src.commons.architectures.rnn_encoder_decoder import Seq2Seq

            input_size = len(
                config["features"]["input"]["fiedls"]
                + config["features"]["input"]["meteo_historical"]
            )
            output_size = len(config["features"]["output"])
            hidden_size = config["architecture"]["hidden"]
            forecast_size = len(config["features"]["input"]["meteo_forecast"])

            output_seq_len = config["features"]["output_seq_len"]

            model = Seq2Seq(
                input_size, output_size, hidden_size, forecast_size, output_seq_len
            )

            return model

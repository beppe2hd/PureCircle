import joblib, sys, os
import matplotlib.pyplot as plt
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.getenv("PYTHONPATH"))
print(os.getenv("PYTHONPATH"))
from src.commons.utils import get_config_file

tests = ['config_season2_MSE_W_allFIleds0',
         'config_season2_MSE_W_allFIleds1',
         'config_season2_MSE_W_allFIleds2',
         'config_season2_MSE_W_allFIleds3',
         'config_season2_MSE_W_allFIleds4',
         'config_season2_MSE_W_allFIleds5',
         'config_season2_MSE_W_allFIleds6',
         'config_season2_MSE_W_allFIleds7']

iter = 0
for test in tests:

    iter += 1

    config = get_config_file(f"src/configurations/{test}.yaml")
    folder_path = "src/weights/" + config["name"] + config["version"].replace(".", "_")
    path_test_output = folder_path + "/test_output.pkl"
    path_test_y = folder_path + "/test_y.pkl"
    y_pred = joblib.load(path_test_output)
    y_true = joblib.load(path_test_y)

    print(config['name'])

    # Plot mean of absolute error
    abs_error = abs(y_pred-y_true)
    meanError = abs_error.mean(dim=0)
    meanError = meanError.detach().cpu().numpy()
    plt.plot(meanError, label=config['name'][25:-1])

    if iter ==1:
       y_diff = abs(y_true-y_true[:,0,:].unsqueeze(1))
       y_diff = y_diff.mean(dim=0)
       plt.plot(y_diff, '.', label='keepSM')
        


plt.title("SM abs Error (mean)"); plt.xlabel("time forecast Horizon"); plt.ylabel("variance")
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()
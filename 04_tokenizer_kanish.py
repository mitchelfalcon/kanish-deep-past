{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "eb09732a",
   "metadata": {
    "_cell_guid": "b1076dfc-b9ad-4769-8c92-a6c4dae69d19",
    "_uuid": "8f2839f25d086af736a60e9eeb907d3b93b6e0e5",
    "execution": {
     "iopub.execute_input": "2025-12-26T04:33:23.586747Z",
     "iopub.status.busy": "2025-12-26T04:33:23.586019Z",
     "iopub.status.idle": "2025-12-26T04:33:25.853066Z",
     "shell.execute_reply": "2025-12-26T04:33:25.852184Z"
    },
    "papermill": {
     "duration": 2.271212,
     "end_time": "2025-12-26T04:33:25.854465",
     "exception": false,
     "start_time": "2025-12-26T04:33:23.583253",
     "status": "completed"
    },
    "tags": []
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "/kaggle/input/kanish/01_extraer.py\n",
      "/kaggle/input/kanish/02_auditoria.py\n",
      "/kaggle/input/kanish/publications.csv\n",
      "/kaggle/input/kanish/04_tokenizer_kanish.py\n",
      "/kaggle/input/kanish/07_cerebro_analitico.py\n",
      "/kaggle/input/kanish/.gitignore\n",
      "/kaggle/input/kanish/03_limpieza_kaggle.py\n",
      "/kaggle/input/kanish/08_entrenar_gliner.py\n",
      "/kaggle/input/kanish/00_populate_graph.py\n",
      "/kaggle/input/kanish/05_pdf_miner.py\n",
      "/kaggle/input/kanish/06_grafo_constructor.py\n",
      "/kaggle/input/kanish/google.colab-0.1.6.vsix\n",
      "/kaggle/input/kanish/01_kanish_export.py\n",
      "/kaggle/input/kanish/09_finetune_nllb.py\n",
      "/kaggle/input/kanish/train.csv\n",
      "/kaggle/input/kanish/reporte_anomalias_kaggle.txt\n",
      "/kaggle/input/kanish/kanish_brain_frozen.json\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/sample_submission.csv\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/bibliography.csv\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/publications.csv\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/Sentences_Oare_FirstWord_LinNum.csv\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/OA_Lexicon_eBL.csv\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/eBL_Dictionary.csv\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/train.csv\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/test.csv\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/published_texts.csv\n",
      "/kaggle/input/kanish/deep-past-initiative-machine-translation/resources.csv\n",
      "/kaggle/input/kanish-knowledge-graph/kanish_brain_frozen.json\n"
     ]
    }
   ],
   "source": [
    "# This Python 3 environment comes with many helpful analytics libraries installed\n",
    "# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python\n",
    "# For example, here's several helpful packages to load\n",
    "\n",
    "import numpy as np # linear algebra\n",
    "import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)\n",
    "\n",
    "# Input data files are available in the read-only \"../input/\" directory\n",
    "# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory\n",
    "\n",
    "import os\n",
    "for dirname, _, filenames in os.walk('/kaggle/input'):\n",
    "    for filename in filenames:\n",
    "        print(os.path.join(dirname, filename))\n",
    "\n",
    "# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using \"Save & Run All\" \n",
    "# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session"
   ]
  }
 ],
 "metadata": {
  "kaggle": {
   "accelerator": "nvidiaTeslaT4",
   "dataSources": [
    {
     "datasetId": 9119281,
     "sourceId": 14287115,
     "sourceType": "datasetVersion"
    },
    {
     "datasetId": 9126059,
     "sourceId": 14296693,
     "sourceType": "datasetVersion"
    }
   ],
   "isGpuEnabled": true,
   "isInternetEnabled": true,
   "language": "python",
   "sourceType": "notebook"
  },
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.13"
  },
  "papermill": {
   "default_parameters": {},
   "duration": 8.538373,
   "end_time": "2025-12-26T04:33:26.272787",
   "environment_variables": {},
   "exception": null,
   "input_path": "__notebook__.ipynb",
   "output_path": "__notebook__.ipynb",
   "parameters": {},
   "start_time": "2025-12-26T04:33:17.734414",
   "version": "2.6.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

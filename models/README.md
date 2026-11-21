# Models

Fine-tuned BERT checkpoints (`finetuned_BERT_epoch_<n>.model`, ~440 MB each) are **not** stored in git.

Place the checkpoint here (or set `DARKNET_MODEL_PATH`) to use the scraper's `--predict` flag.
The checkpoints are PyTorch `state_dict`s for `BertForSequenceClassification` (`bert-base-uncased`, 4 labels)
produced by `trainer/notebooks/02_train_validate_predict.ipynb`.

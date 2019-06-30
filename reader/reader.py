from torch.utils.data import DataLoader
import logging

import formatter as form
from dataset import dataset_list

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.WARN)

logger = logging.getLogger(__name__)

collate_fn = {}
formatter = {}


def init_formatter(config, task_list, *args, **params):
    for task in task_list:
        formatter[task] = form.init_formatter(config, task, *args, **params)

        def temp_collate_fn(data):
            return formatter[task].process(data)

        collate_fn[task] = temp_collate_fn


def init_one_dataset(config, mode, *args, **params):
    temp_mode = mode
    try:
        config.get("reader", "%s_dataset_type" % temp_mode)
    except Exception as e:
        logger.warning(
            "[reader] %s_dataset_type has not been defined in config file, use [dataset] train_dataset_type instead." % temp_mode)
        temp_mode = "train"
    which = config.get("dataset", "%s_dataset_type" % temp_mode)

    if which in dataset_list:
        dataset = dataset_list[which](config, mode, *args, **params)
        batch_size = config.getint("train", "batch_size")
        shuffle = config.getbollean("train", "shuffle")
        reader_num = config.getint("train", "reader_num")
        if mode in ["valid", "test"]:
            try:
                batch_size = config.getint("eval", "batch_size")
            except Exception as e:
                logger.warning("[eval] batch size has not been defined in config file, use [train] batch_size instead.")

            try:
                shuffle = config.getboolean("eval", "shuffle")
            except Exception as e:
                shuffle = False
                logger.warning("[eval] shuffle has not been defined in config file, use false as default.")
            try:
                batch_size = config.getint("eval", "reader_num")
            except Exception as e:
                logger.warning("[eval] reader num has not been defined in config file, use [train] reader num instead.")

        dataloader = DataLoader(dataset=dataset,
                                batch_size=batch_size,
                                shuffle=shuffle,
                                num_workers=reader_num,
                                collate_fn=collate_fn[mode],
                                drop_last=False)

        return dataloader
    else:
        raise NotImplementedError


def init_test_dataset(config, *args, **params):
    init_formatter(config, ["test"], *args, **params)
    test_dataset = init_one_dataset(config, "test", *args, **params)

    return test_dataset


def init_dataset(config, *args, **params):
    init_formatter(config, ["train", "valid"], *args, **params)
    train_dataset = init_one_dataset(config, "train", *args, **params)
    valid_dataset = init_one_dataset(config, "valid", *args, **params)

    return train_dataset, valid_dataset


if __name__ == "__main__":
    pass
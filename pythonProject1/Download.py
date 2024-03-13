import fiftyone as fo
import fiftyone.zoo as foz
from pathlib import Path


def test():
    #
    # Only the required images will be downloaded (if necessary).
    # By default, only detections are loaded
    # Download bus, car, truck, bicycle, motorcycle data from cocodataset

    dataset = foz.load_zoo_dataset(
        "coco-2017",
        splits=["validation", "train"],
        classes=["bus", "car", "truck", "bicycle", "motorcycle"],
        # max_samples=50,
    )

    # Visualize the dataset in the FiftyOne App
    session = fo.launch_app(dataset)


if __name__ == '__main__':
    test()

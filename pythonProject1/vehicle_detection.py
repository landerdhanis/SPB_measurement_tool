import cv2
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

if __name__ == "__main__":

    print("test1")
    # Define the model architecture
    class MultiLabelClassifier(nn.Module):
        def __init__(self, num_classes):
            super(MultiLabelClassifier, self).__init__()
            self.base_model = models.resnet50(pretrained=False, num_classes=1000)
            self.fc = nn.Linear(1000, num_classes)

        def forward(self, x):
            features = self.base_model(x)
            out = self.fc(features)
            return torch.sigmoid(out)

    print("test2")
    # Load the trained model
    model = MultiLabelClassifier(num_classes=5)
    model.load_state_dict(torch.load('model.pth', map_location=torch.device('cpu')))
    model.eval()

    # Define the classes
    classes = ['car', 'truck', 'bicycle', 'motorcycle', 'bus']

    # Define the image transformation
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    print("test3")

    # Function to perform inference on camera frames
    def classify_camera_frame(frame):
        image = Image.fromarray(frame)
        image = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(image)
            predicted_labels = (outputs > 0.5).squeeze(0)

        labels = [classes[i] for i, predicted in enumerate(predicted_labels) if predicted]
        return labels


    print("test4")
    # Open the camera feed
    camera = cv2.VideoCapture(0)

    while True:
        ret, frame = camera.read()

        # Perform inference on the current frame
        labels = classify_camera_frame(frame)

        # Display the labels on the frame
        cv2.putText(frame, ', '.join(labels), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow('Camera', frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the window
    camera.release()
    cv2.destroyAllWindows()
from XRPLib.encoder import Encoder

# Test Right Encoder
print("Testing Right Encoder")
right_motor_encoder = Encoder(1, 12, 13)
print("Right Encoder Initialized")

# Test Left Encoder
print("Testing Left Encoder")
left_motor_encoder = Encoder(0, 4, 5)
print("Left Encoder Initialized")

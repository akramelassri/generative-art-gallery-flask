from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup
import os

# Helper functions
def get_valid_path():
    """Get valid file path from user"""
    while True:
        path = input("Enter the path to your audio file (mp3/wav): ").strip()
        if os.path.exists(path):
            return path
        print("File not found. Please try again.")

def load_audio(path):
    """Load audio from wav or mp3 file"""
    try:
        return AudioSegment.from_file(path)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

# Audio processing functions
def cutting(audio):
    """Cut a segment from the audio"""
    try:
        start = float(input('Enter start time (seconds): ')) * 1000
        end = float(input('Enter end time (seconds): ')) * 1000
        return audio[start:end]
    except ValueError:
        print("Invalid time format. Using full audio.")
        return audio

def change_speed(audio):
    """Change audio playback speed"""
    try:
        speed_factor = float(input('Enter speed factor (0.5-2.0): '))
        return speedup(audio, speed_factor)
    except ValueError:
        print("Invalid speed factor. Using normal speed.")
        return audio

def mix_audios(audio):
    """Mix another audio file with current audio"""
    print("\nSelect audio to mix with:")
    mix_path = get_valid_path()
    mix_audio = load_audio(mix_path)
    
    try:
        position = float(input('Enter mix position (seconds): ')) * 1000
        return audio.overlay(mix_audio, position=int(position))
    except ValueError:
        print("Invalid position. Using default position 0.")
        return audio.overlay(mix_audio)

def reverse_audio(audio):
    """Reverse the audio"""
    return audio.reverse()

# History management functions
def add_to_history(history, current_index, new_audio):
    """Add new state to history and truncate future states"""
    # Truncate history if we're not at the end
    if current_index < len(history) - 1:
        history = history[:current_index + 1]
    history.append(new_audio)
    return history, current_index + 1

def load_audio_with_history():
    """Load initial audio and initialize history"""
    while True:
        path = get_valid_path()
        original_audio = load_audio(path)
        if original_audio:
            return [original_audio], 0  # Initialize history and index

# Main application
def main():
    history = []
    current_index = -1
    original_audio = None

    while True:
        if current_index >= 0:
            current_audio = history[current_index]
        else:
            current_audio = None

        print("\n=== Audio Editor ===")
        print(f"Current history position: {current_index + 1}/{len(history)}")
        print("1. Load an audio")
        print("2. Play current audio")
        print("3. Cut audio")
        print("4. Change speed")
        print("5. Mix with another audio")
        print("6. Reverse audio")
        print("7. Save audio")
        print("8. Undo")
        print("9. Redo")
        print("10. Reset to original")
        print("11. Add original audio")
        print("11. Exit")

        choice = input("\nChoose an option (1-11): ")

        if choice == '2':
            if current_audio:
                play(current_audio)
            else:
                print("No audio loaded to play.")
        elif choice == '1':
            history, current_index = load_audio_with_history()
            original_audio = history[0]
        elif choice == '3':
            if current_audio:
                new_audio = cutting(current_audio)
                if new_audio != current_audio:
                    history, current_index = add_to_history(history, current_index, new_audio)
            else:
                print("No audio loaded to cut.")
        elif choice == '4':
            if current_audio:
                new_audio = change_speed(current_audio)
                history, current_index = add_to_history(history, current_index, new_audio)
            else:
                print("No audio loaded to modify speed.")
        elif choice == '5':
            if current_audio:
                new_audio = mix_audios(current_audio)
                history, current_index = add_to_history(history, current_index, new_audio)
            else:
                print("No audio loaded to mix.")
        elif choice == '6':
            if current_audio:
                new_audio = reverse_audio(current_audio)
                history, current_index = add_to_history(history, current_index, new_audio)
            else:
                print("No audio loaded to reverse.")
        elif choice == '7':
            if current_audio:
                output_format = input("Enter output format (wav/mp3): ").lower()
                output_name = input("Enter output file name (without extension): ")
                current_audio.export(f"{output_name}.{output_format}", format=output_format)
                print("Audio saved successfully!")
            else:
                print("No audio loaded to save.")
        elif choice == '8':  # Undo
            if current_index > 0:
                current_index -= 1
                print(f"Undo to step {current_index + 1}")
            else:
                print("Already at earliest state")
        elif choice == '9':  # Redo
            if current_index < len(history) - 1:
                current_index += 1
                print(f"Redo to step {current_index + 1}")
            else:
                print("Already at latest state")
        elif choice == '10':  # Reset to original
            if original_audio:
                history = [original_audio]
                current_index = 0
                print("Reset to original audio")
            else:
                print("No original audio loaded.")
        elif choice == '11':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1-11.")

if __name__ == "__main__":
    main()
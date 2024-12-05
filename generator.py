import PyPDF2
import nltk
import random
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Dict

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

class PreciseFlashcardGenerator:
    def __init__(self, pdf_path):
        """Initialize the precise flashcard generator."""
        self.pdf_path = pdf_path
        self.flashcards = []
    
    def extract_text(self):
        """Extract clean text from PDF."""
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ' '.join(page.extract_text() for page in reader.pages)
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,?!-]', '', text)
        
        return text
    
    def generate_flashcards(self, max_cards=50):
        """Generate precise flashcards with more meaningful questions."""
        text = self.extract_text()
        sentences = nltk.sent_tokenize(text)
        
        self.flashcards = []
        while len(self.flashcards) < max_cards and sentences:
            sentence = sentences.pop(random.randint(0, len(sentences)-1))
            
            # Different types of flashcard generation
            card_generators = [
                self._create_definition_card,
                self._create_key_concept_card,
                self._create_fill_blank_card
            ]
            
            generator = random.choice(card_generators)
            card = generator(sentence)
            
            if card:
                self.flashcards.append(card)
    
    def _create_definition_card(self, sentence):
        """Create a definition-style flashcard."""
        # Look for sentences that define or explain a concept
        definition_patterns = [
            r'(\w+)\s+is\s+defined\s+as\s+(.*?)[\.,]',
            r'(\w+)\s+means\s+(.*?)[\.,]',
            r'A\s+(\w+)\s+is\s+(.*?)[\.,]'
        ]
        
        for pattern in definition_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                term, definition = match.groups()
                return {
                    'type': 'definition',
                    'question': f"Define {term}",
                    'answer': definition.strip()
                }
        
        return None
    
    def _create_key_concept_card(self, sentence):
        """Create a key concept question card."""
        # Look for key terms and their context
        tagged_words = nltk.pos_tag(nltk.word_tokenize(sentence))
        
        # Prioritize nouns and proper nouns
        key_terms = [word for word, pos in tagged_words if pos in ['NN', 'NNP', 'NNS']]
        
        if key_terms:
            term = random.choice(key_terms)
            return {
                'type': 'concept',
                'question': f"Explain the significance of {term} in the context of the text",
                'answer': sentence
            }
        
        return None
    
    def _create_fill_blank_card(self, sentence):
        """Create a fill-in-the-blank card with careful word selection."""
        words = nltk.word_tokenize(sentence)
        tagged_words = nltk.pos_tag(words)
        
        # Filter out less meaningful words and very short/long words
        candidate_words = [
            word for word, pos in tagged_words 
            if pos not in ['DT', 'IN', 'CC', 'WDT'] 
            and 3 < len(word) < 15 
            and not word[0].islower()
        ]
        
        if not candidate_words:
            return None
        
        # Prioritize nouns, proper nouns, and key terms
        blank_word = random.choice(candidate_words)
        
        # Create the question with the blank
        question = sentence.replace(blank_word, '______')
        
        return {
            'type': 'fill_blank',
            'question': question,
            'answer': blank_word
        }

class FlashcardApp:
    def __init__(self, master, flashcards):
        self.master = master
        master.title("Interactive Flashcards")
        master.geometry("600x400")
        
        self.flashcards = flashcards
        self.current_card_index = 0
        
        # Question display
        self.question_label = tk.Label(master, text="", font=("Arial", 14), wraplength=500)
        self.question_label.pack(pady=20)
        
        # Answer button
        self.show_answer_button = tk.Button(master, text="Show Answer", command=self.show_answer)
        self.show_answer_button.pack(pady=10)
        
        # Answer display (initially hidden)
        self.answer_label = tk.Label(master, text="", font=("Arial", 12), wraplength=500)
        self.answer_label.pack(pady=10)
        
        # Navigation buttons
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)
        
        self.prev_button = tk.Button(button_frame, text="Previous", command=self.previous_card)
        self.prev_button.pack(side=tk.LEFT, padx=10)
        
        self.next_button = tk.Button(button_frame, text="Next", command=self.next_card)
        self.next_button.pack(side=tk.LEFT, padx=10)
        
        # Card type label
        self.card_type_label = tk.Label(master, text="", font=("Arial", 10))
        self.card_type_label.pack(pady=5)
        
        # Initialize first card
        self.show_card()
    
    def show_card(self):
        # Reset answer visibility
        self.answer_label.config(text="")
        self.show_answer_button.config(state=tk.NORMAL)
        
        # Show current card details
        card = self.flashcards[self.current_card_index]
        self.question_label.config(text=card['question'])
        self.card_type_label.config(text=f"Card Type: {card.get('type', 'Default')}")
    
    def show_answer(self):
        card = self.flashcards[self.current_card_index]
        self.answer_label.config(text=card['answer'])
        self.show_answer_button.config(state=tk.DISABLED)
    
    def next_card(self):
        self.current_card_index = (self.current_card_index + 1) % len(self.flashcards)
        self.show_card()
    
    def previous_card(self):
        self.current_card_index = (self.current_card_index - 1) % len(self.flashcards)
        self.show_card()

def main():
    # Select PDF file
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    pdf_path = filedialog.askopenfilename(
        title="Select PDF File",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    if not pdf_path:
        messagebox.showerror("Error", "No PDF file selected")
        return
    
    # Generate flashcards
    generator = PreciseFlashcardGenerator(pdf_path)
    generator.generate_flashcards(max_cards=50)
    
    # Create flashcard review app
    root = tk.Tk()
    app = FlashcardApp(root, generator.flashcards)
    root.mainloop()

if __name__ == '__main__':
    main()
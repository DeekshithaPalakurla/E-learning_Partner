import PyPDF2
import nltk
import random
import re
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import List, Dict

# Ensure NLTK resources are downloaded
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)

class AdvancedQuizGenerator:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.questions = []
        self.full_text = self.extract_text()
        self.sentences = nltk.sent_tokenize(self.full_text) if self.full_text else []
    
    def extract_text(self):
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ' '.join(page.extract_text() for page in reader.pages)
            
            # Clean text
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'[^\w\s.,?!-]', '', text)
            
            return text.strip()
        except Exception as e:
            messagebox.showerror("PDF Error", f"Could not read PDF: {e}")
            return ""
    
    def generate_quiz(self, num_questions=10):
        question_generators = [
            self._safe_create_key_concept_question,
            self._safe_create_definition_question,
            self._safe_create_fill_blank_question,
            self._safe_create_relationship_question
        ]
        
        self.questions = []
        attempts = 0
        max_attempts = 100
        
        while len(self.questions) < num_questions and attempts < max_attempts:
            generator = random.choice(question_generators)
            question = generator()
            if question and len(self.questions) < num_questions:
                self.questions.append(question)
            attempts += 1
        
        self.questions = self.questions[:num_questions]
    
    def _safe_create_key_concept_question(self):
        try:
            return self._create_key_concept_question()
        except Exception:
            return None
    
    def _safe_create_definition_question(self):
        try:
            return self._create_definition_question()
        except Exception:
            return None
    
    def _safe_create_fill_blank_question(self):
        try:
            return self._create_contextual_fill_blank_question()
        except Exception:
            return None
    
    def _safe_create_relationship_question(self):
        try:
            return self._create_relationship_question()
        except Exception:
            return None
    
    def _create_key_concept_question(self):
        """Generate more nuanced key concept questions with better options."""
        if not self.sentences:
            return None
        
        # Use NLTK to extract more meaningful key terms
        words = nltk.word_tokenize(' '.join(self.sentences))
        tagged_words = nltk.pos_tag(words)
        
        # Focus on nouns and proper nouns
        key_terms = [
            word for word, pos in tagged_words 
            if pos in ['NN', 'NNP', 'NNPS'] and len(word) > 3
        ]
        
        if not key_terms:
            return None
        
        key_term = random.choice(key_terms)
        
        # Context-aware question generation
        context_sentences = [
            sent for sent in self.sentences 
            if key_term in sent
        ]
        
        # Create more specific question
        question_templates = [
            f"In the context of the given text, what is the significance of {key_term}?",
            f"How does {key_term} contribute to the main ideas discussed in the document?",
            f"What role does {key_term} play in the broader discussion?",
            f"Explain the importance of {key_term} based on the text's context."
        ]
        
        question = random.choice(question_templates)
        
        # Generate more contextually relevant options
        options = [
            f"{key_term} is a critical concept that illustrates key themes",
            f"{key_term} provides essential context for understanding the text's main arguments",
            f"{key_term} represents a pivotal idea that connects multiple concepts",
            f"{key_term} offers insights into the underlying principles discussed"
        ]
        
        return {
            'type': 'key_concept',
            'question': question,
            'options': options,
            'correct_answer': options[0]
        }
    
    def _create_definition_question(self):
        """Generate more sophisticated definition-based questions."""
        definition_patterns = [
            r'(\w+)\s+is\s+defined\s+as\s+(.*?)[\.,;]',
            r'(\w+)\s+means\s+(.*?)[\.,;]',
            r'A\s+(\w+)\s+is\s+(.*?)[\.,;]'
        ]
        
        # Use NLTK to get more precise terms
        words = nltk.word_tokenize(' '.join(self.sentences))
        tagged_words = nltk.pos_tag(words)
        
        # Focus on nouns with some context
        candidate_terms = [
            word for word, pos in tagged_words 
            if pos in ['NN', 'NNP', 'NNPS'] and 3 < len(word) < 20
        ]
        
        for pattern in definition_patterns:
            matches = [re.search(pattern, sent, re.IGNORECASE) for sent in self.sentences]
            valid_matches = [m for m in matches if m]
            
            if valid_matches:
                match = random.choice(valid_matches)
                term, definition = match.groups()
                
                # More sophisticated question templates
                question_templates = [
                    f"Based on the text, what is the precise definition of {term}?",
                    f"How would you most accurately describe {term}?",
                    f"What definition best captures the essence of {term}?",
                    f"Select the most comprehensive description of {term}."
                ]
                
                question_text = random.choice(question_templates)
                
                # Generate more thoughtful options
                options = [
                    definition.strip(),
                    f"A comprehensive explanation of {term}'s key characteristics",
                    f"The fundamental concept underlying {term}",
                    f"A nuanced interpretation of {term}'s meaning"
                ]
                
                # Ensure some variety in options
                while len(set(options)) < 4:
                    distractor = random.choice(self.sentences)
                    if term not in distractor:
                        options.append(f"A contextual description related to {term}")
                
                random.shuffle(options)
                
                return {
                    'type': 'definition',
                    'question': question_text,
                    'options': options,
                    'correct_answer': definition.strip()
                }
        
        return None

    def _create_contextual_fill_blank_question(self):
        """Create more sophisticated fill-in-the-blank questions with context."""
        tagged_sentences = [nltk.pos_tag(nltk.word_tokenize(sent)) for sent in self.sentences]
        
        # More sophisticated word selection
        candidate_words = [
            word for sent in tagged_sentences 
            for word, pos in sent 
            if pos in ['NN', 'NNP', 'JJ', 'VB'] 
            and 3 < len(word) < 15
            and not word.lower() in ['the', 'a', 'an']
        ]
        
        if not candidate_words:
            return None
        
        target_word = random.choice(candidate_words)
        
        # More context-rich sentence selection
        context_sentences = [
            sent for sent in self.sentences 
            if target_word in sent and len(sent.split()) > 5
        ]
        
        if not context_sentences:
            return None
        
        base_sentence = random.choice(context_sentences)
        
        # More sophisticated question templates
        question_templates = [
            f"In the context of the discussion, complete the following: {base_sentence.replace(target_word, '______')}",
            f"Fill in the blank with the most appropriate term: {base_sentence.replace(target_word, '______')}",
            f"Which word best completes this sentence: {base_sentence.replace(target_word, '______')}",
            f"Select the term that most precisely fits in this context: {base_sentence.replace(target_word, '______')}"
        ]
        
        question_text = random.choice(question_templates)
        
        # Generate options with more thought
        options = [target_word]
        while len(options) < 4:
            distractor = random.choice(candidate_words)
            if distractor not in options:
                options.append(distractor)
        
        random.shuffle(options)
        
        return {
            'type': 'fill_blank',
            'question': question_text,
            'options': options,
            'correct_answer': target_word
        }

    def _create_relationship_question(self):
        """Generate more sophisticated relationship questions."""
        # Advanced NLP-based relationship extraction
        tagged_sentences = [nltk.pos_tag(nltk.word_tokenize(sent)) for sent in self.sentences]
        
        # Find meaningful noun pairs with context
        noun_pairs = []
        for sent in tagged_sentences:
            nouns = [word for word, pos in sent if pos in ['NN', 'NNP', 'NNPS']]
            for i in range(len(nouns)-1):
                if nouns[i] != nouns[i+1]:
                    noun_pairs.append((nouns[i], nouns[i+1]))
        
        if not noun_pairs:
            return None
        
        # Select a meaningful noun pair
        noun1, noun2 = random.choice(noun_pairs)
        
        # More sophisticated relationship question templates
        question_templates = [
            f"Describe the connection between {noun1} and {noun2} based on the text's context.",
            f"How are {noun1} and {noun2} related in the context of the discussion?",
            f"Analyze the relationship between {noun1} and {noun2} as presented in the text.",
            f"What inference can be drawn about the interaction of {noun1} and {noun2}?"
        ]
        
        question_text = random.choice(question_templates)
        
        # Generate more nuanced relationship options
        options = [
            f"{noun1} provides context or framework for understanding {noun2}",
            f"{noun1} and {noun2} represent interconnected concepts",
            f"{noun1} influences or impacts the understanding of {noun2}",
            f"{noun1} and {noun2} are complementary or comparative elements"
        ]
        
        random.shuffle(options)
        
        return {
            'type': 'relationship',
            'question': question_text,
            'options': options,
            'correct_answer': options[0]
        }

class QuizApp:
    def __init__(self, master, questions):
        self.master = master
        master.title("Interactive Quiz")
        master.geometry("600x500")
        
        self.questions = questions
        self.current_question_index = 0
        self.score = 0
        
        # Question label
        self.question_label = tk.Label(master, text="", font=("Arial", 14), wraplength=550, justify=tk.LEFT)
        self.question_label.pack(pady=20)
        
        # Type label
        self.type_label = tk.Label(master, text="", font=("Arial", 10))
        self.type_label.pack(pady=5)
        
        # Option buttons
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(master, text="", font=("Arial", 12), wraplength=500, 
                            command=lambda idx=i: self.check_answer(idx))
            btn.pack(pady=5)
            self.option_buttons.append(btn)
        
        # Result label
        self.result_label = tk.Label(master, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)
        
        # Navigation buttons
        nav_frame = tk.Frame(master)
        nav_frame.pack(pady=10)
        
        tk.Button(nav_frame, text="Previous", command=self.previous_question).pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Next", command=self.next_question).pack(side=tk.LEFT, padx=10)
        
        # Score display
        self.score_label = tk.Label(master, text="Score: 0/0", font=("Arial", 12))
        self.score_label.pack(pady=10)
        
        # Initialize first question
        self.display_question()
    
    def display_question(self):
        # Reset result label
        self.result_label.config(text="")
        
        # Get current question
        current_q = self.questions[self.current_question_index]
        
        # Update question and type labels
        self.question_label.config(text=current_q['question'])
        self.type_label.config(text=f"Question Type: {current_q['type']}")
        
        # Update option buttons
        for i, option in enumerate(current_q['options']):
            self.option_buttons[i].config(text=option, state=tk.NORMAL)
        
        # Update score display
        self.score_label.config(text=f"Score: {self.score}/{self.current_question_index + 1}")
    
    def check_answer(self, selected_index):
        current_q = self.questions[self.current_question_index]
        selected_option = current_q['options'][selected_index]
        
        if selected_option == current_q['correct_answer']:
            self.result_label.config(text="Correct!", fg="green")
            self.score += 1
        else:
            self.result_label.config(text=f"Wrong. Correct answer was: {current_q['correct_answer']}", fg="red")
        
        # Disable buttons after answering
        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)
        
        # Update score display
        self.score_label.config(text=f"Score: {self.score}/{self.current_question_index + 1}")
    
    def previous_question(self):
        self.current_question_index = (self.current_question_index - 1) % len(self.questions)
        self.display_question()
    
    def next_question(self):
        self.current_question_index = (self.current_question_index + 1) % len(self.questions)
        self.display_question()

def main():
    # Initialize Tk root
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        # Select PDF file
        pdf_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not pdf_path:
            messagebox.showerror("Error", "No PDF file selected")
            return
        
        # Explicitly bring dialog to front and ensure it's visible
        root.deiconify()
        root.lift()
        root.focus_force()
        
        
        # Number of questions
        num_questions = simpledialog.askinteger(
            "Quiz Configuration", 
            "How many questions would you like?", 
            minvalue=5, 
            maxvalue=50, 
            initialvalue=10
        )
        
        # Hide root again
        root.withdraw()
        
        if not num_questions:
            messagebox.showinfo("Quiz", "Quiz generation cancelled.")
            return
        
        # Generate quiz
        quiz_generator = AdvancedQuizGenerator(pdf_path)
        quiz_generator.generate_quiz(num_questions)
        
        # Launch quiz app
        root = tk.Tk()
        app = QuizApp(root, quiz_generator.questions)
        root.mainloop()
    
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    finally:
        # Ensure root window is closed
        if 'root' in locals():
            root.destroy()

if __name__ == '__main__':
    main()
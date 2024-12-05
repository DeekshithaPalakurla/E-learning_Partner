import PyPDF2
import nltk
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from heapq import nlargest

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class PDFSummarizer:
    def __init__(self, pdf_path):
        """Initialize PDF summarizer."""
        self.pdf_path = pdf_path
        self.stop_words = set(stopwords.words('english'))
    
    def extract_text(self):
        """Extract text from PDF."""
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ' '.join(page.extract_text() for page in reader.pages)
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text
    
    def summarize(self, summary_length=3):
        """Generate a meaningful summary of the PDF."""
        # Extract and preprocess text
        text = self.extract_text()
        sentences = sent_tokenize(text)
        
        # Tokenize and clean words
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalnum() and word not in self.stop_words]
        
        # Calculate word frequencies
        word_frequencies = FreqDist(words)
        
        # Score sentences based on word frequencies
        sentence_scores = {}
        for sentence in sentences:
            for word in word_tokenize(sentence.lower()):
                if word in word_frequencies:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_frequencies[word]
                    else:
                        sentence_scores[sentence] += word_frequencies[word]
        
        # Select top sentences for summary
        summary_sentences = nlargest(
            summary_length, 
            sentence_scores, 
            key=sentence_scores.get
        )
        
        # Reconstruct summary maintaining original sentence order
        summary = []
        for sent in sentences:
            if sent in summary_sentences:
                summary.append(sent)
        
        return ' '.join(summary)
    
    def key_topics(self, num_topics=5):
        """Extract key topics from the PDF."""
        text = self.extract_text()
        words = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        words = [word for word in words if 
                 word.isalpha() and 
                 word not in self.stop_words and 
                 len(word) > 2]
        
        # Calculate word frequencies
        word_freq = FreqDist(words)
        
        # Return top topics
        return word_freq.most_common(num_topics)

def show_summary_popup(summary, topics):
    """Create a popup window to display summary and key topics."""
    # Create popup window
    popup = tk.Tk()
    popup.title("PDF Summary")
    popup.geometry("500x400")
    
    # Summary frame
    summary_frame = tk.Frame(popup)
    summary_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Summary label
    summary_label = tk.Label(summary_frame, text="Summary:", font=("Helvetica", 12, "bold"))
    summary_label.pack(anchor='w')
    
    # Summary text widget
    summary_text = tk.Text(summary_frame, wrap=tk.WORD, height=10)
    summary_text.insert(tk.END, summary)
    summary_text.config(state=tk.DISABLED)
    summary_text.pack(fill=tk.BOTH, expand=True)
    
    # Topics frame
    topics_frame = tk.Frame(popup)
    topics_frame.pack(padx=10, pady=10, fill=tk.X)
    
    # Topics label
    topics_label = tk.Label(topics_frame, text="Key Topics:", font=("Helvetica", 12, "bold"))
    topics_label.pack(anchor='w')
    
    # Topics listbox
    topics_listbox = tk.Listbox(topics_frame)
    for topic, freq in topics:
        topics_listbox.insert(tk.END, f"{topic}: {freq}")
    topics_listbox.pack(fill=tk.X)
    
    # Close button
    close_button = tk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)
    
    popup.mainloop()

def main():
    # Create root window (will be hidden)
    root = tk.Tk()
    root.withdraw()
    
    # Open file dialog to select PDF
    pdf_path = filedialog.askopenfilename(
        title="Select PDF File",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    # Check if a file was selected
    if not pdf_path:
        messagebox.showinfo("Info", "No file selected. Exiting.")
        return
    
    try:
        # Create summarizer
        summarizer = PDFSummarizer(pdf_path)
        
        # Generate summary
        summary = summarizer.summarize()
        
        # Get key topics
        topics = summarizer.key_topics()
        
        # Show summary in popup
        show_summary_popup(summary, topics)
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
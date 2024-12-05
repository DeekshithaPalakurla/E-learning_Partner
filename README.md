## E-Learning Partner

## Findings and Model Performance

What Went Well: The project successfully extracted meaningful text from PDFs and generated high-quality summaries, quizzes, and flashcards. The interactive GUI for quizzes and flashcards enhanced usability and made the learning process engaging.

Challenges: Handling poorly formatted PDFs with inconsistent text extraction was a significant challenge. Generating diverse yet contextually accurate questions required careful tuning of the question generation logic.

Revealed Insights: The models demonstrated that NLP techniques like tokenization, frequency analysis, and POS tagging are effective for extracting key content and generating educational materials.

What I Learned: The importance of preprocessing for improving text quality and how NLP libraries like NLTK facilitate robust text analysis. GUI integration added user interactivity, enhancing the overall experience.

Future Improvements:
Implementing deep learning-based models for better summarization and question generation.
Improving support for PDFs with images, tables, or non-text elements.
Expanding compatibility to other document formats like Word or HTML.
Adding personalization features, such as tailoring flashcards and quizzes based on difficulty or topic preferences.


## To test

pip install -r requirements.txt
python generator.py (flashcards generator)
python quiz_gen.py (quizzes generator)
python summarizer.py (text summary generator)
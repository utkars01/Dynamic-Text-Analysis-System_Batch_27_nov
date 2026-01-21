"""
Word cloud generation utility for AI Narrative Nexus.

Generates a static PNG word cloud from aggregated tokens.
This is document-level and non-interactive by design.
"""

from pathlib import Path
from wordcloud import WordCloud


def generate_wordcloud(tokens, output_path: Path):
    """
    Generate and save a word cloud image.

    Args:
        tokens (List[str]): aggregated tokens from document
        output_path (Path): where PNG should be saved
    """
    if not tokens:
        return

    text = " ".join(tokens)

    wc = WordCloud(
        width=1000,
        height=500,
        background_color="white",
        max_words=200,
        collocations=False
    )

    wc.generate(text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wc.to_file(str(output_path))

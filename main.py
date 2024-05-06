import yt_dlp as youtube_dl, logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


logger = logging.getLogger(__name__)

def make_words(filepath):
    
    with open(filepath, 'r') as f:
        lines = f.readlines()

    words = []  # List to store all words

    in_text_block = False

    counter = 0

    for line in lines:
        line = line.strip()
        if line.isdigit():  # Check if line is a number (indicating new subtitle block)
            in_text_block = False
        elif "<" in line:
            continue
        elif '-->' in line:  # Check if line contains time stamps (indicating new subtitle block)
            in_text_block = True
        elif in_text_block and line:  # Check if line is non-empty and within a text block
            # Remove any <c> tags and split line into words
            if counter % 2 == 0:
                words.extend(line.split())
            counter += 1


    # Save all words into a file
    words_file = f'{filepath.split("?v=")[-1]}.txt'
    with open(words_file, 'w') as wf:
        wf.write(' '.join(words))
    
    return words
        
def download_subtitles(filepath):
    """Download Single Video and Subtitles

    Args:
        args (_type_, optional): _description_. Defaults to None.
    """

    video_id = filepath.split("?v=")[-1]
    # Download subtitles with specified options
    ydl_subtitles_opts = {
        'skip_download': True,  # We only want the subtitles
        'writeautomaticsub': True,
        'outtmpl': f'data/{video_id}.srt'
    }

    # Download subtitles
    with youtube_dl.YoutubeDL(ydl_subtitles_opts) as ydl:
        try:
            ydl.download([filepath])
        except youtube_dl.utils.DownloadError:
            logger.info(f"No subtitles on {filepath}. Skipping.")

    return make_words(filepath=f'data/{video_id}.srt.en.vtt')

def perform_rag(words):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(words)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(words)
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())


        
def main():
    url = "https://www.youtube.com/watch?v=BBAuhqvT_ds"
    words = download_subtitles(filepath=url)


if __name__ == "__main__":
    main()
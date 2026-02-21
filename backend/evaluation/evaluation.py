from jiwer import wer
import sacrebleu

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

# ASR
asr_ref = read_file("asr_reference.txt")
asr_hyp = read_file("asr_hypothesis.txt")

print("ASR WER:", wer(asr_ref, asr_hyp))

# MT
mt_ref = read_file("mt_reference.txt")
mt_hyp = read_file("mt_hypothesis.txt")

bleu = sacrebleu.corpus_bleu(mt_hyp, [mt_ref])
print("MT BLEU:", bleu.score)
'''
    Script that converts set of MIDI files into dictionary mapping from path of each file to the list of notes in it.
    The dictionary is saved in pickle format, so it can be easily used further without the need to redo the pre-processing again.
    This script takes advantage of concurrency in Python to speed up the runtime.

'''

import glob
import pickle
import time
import concurrent
from tqdm import tqdm
from music21 import converter, instrument, note, chord

def extract_notes(path):
    ''' Extract notes from a single MIDI file'''
    notes = []
    # print("Parsing %s" % filepath)

    midi = converter.parse(path)

    notes_to_parse = None

    try: # file has instrument parts
        s2 = instrument.partitionByInstrument(midi)
        notes_to_parse = s2.parts[1].recurse() 
    except: # file has notes in a flat structure
        notes_to_parse = midi.flat.notes

    for element in notes_to_parse:
        if isinstance(element, note.Note):
            notes.append(str(element.pitch))
        elif isinstance(element, chord.Chord):
            notes.append('.'.join(str(n) for n in element.normalOrder))
            
    print(f'"{path}" completed')

    return notes

def main():
    """ Get all the notes and chords from the midi files"""

    t1 = time.perf_counter()
    #get paths
    paths = glob.glob(r"data\classical_composers\midi\*\*.mid")
    paths = [path.replace('\\','/') for path in paths]

    print(f'Converting {len(paths)} MIDI files into text format:')
    time.sleep(1)

    #run pre-processing
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(extract_notes, paths), total=len(paths)))

    #organize data into a dictionary
    notes_dict = {}
    for i in range(len(results)):
        notes_dict[paths[i]] = results[i]

    #save results
    with open('data/notes', 'wb') as f:
        pickle.dump(notes_dict, f)

    #print time elapsed
    t2 = time.perf_counter()
    print(f'Finished in {t2-t1} seconds')

#run script
if __name__ == '__main__':
    main()
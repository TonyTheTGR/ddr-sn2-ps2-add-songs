# DDR X (USA) backend — first milestone

This branch introduces `ddrx.py`, a **read-only** DDR X resource
inspector. The SuperNOVA 2 converter (`sn2.py`), its GUI, and conversion
utilities remain unchanged.

## Verified

- USA executable: `SLUS_217.67`
- Archives: `SYSTEM.DAT`, `IMAGE.DAT`, `SOUND.DAT`, `MDB_X1.DAT`
- SuperNOVA 2's executable file-table parser recognizes DDR X resource entries
- Song chart pack: `mdb/csq_all.bin`; artwork pack: `mdb/music_dt.bin`
- Music resources: `MUSIC/<code>.vig` and `SEL/<code>_s.vig`
- Local test using the submitted DDR X executable recovered **77 paired audio slots**
- The shared chart reader recognized stock DDR X charts in previous analysis

## Usage

```powershell
py ddrx.py inspect "D:\Games\Dance Dance Revolution X (USA).iso" --json ddrx_inventory.json
py -m unittest test_ddrx.py
```

The project still requires its usual Python dependencies, including NumPy.

## Safety gates / remaining tasks

- No modified ISO output or DDR X song replacement is implemented.
- DDR X song-record metadata and difficulty fields need mapping before writes.
- Do **not** reuse the SN2 1–10 rating conversion for DDR X's X-scale levels.
- Shock Arrow encoding needs independent verification; never silently discard mines.
- Audio encoding and archive relocation require controlled boot testing.

The existing SuperNOVA 2 flow remains untouched.

# DDR Extreme 2 (USA): research backend

This branch is independent from the DDR X converter. The first, read-only
research toolkit is distributed as `extreme2_research_toolkit_v0_1.zip` in the
ChatGPT project conversation; it is **not** yet committed as source here.

## Confirmed by the user-supplied ISO report and probe

- Executable: `SLUS_211.74`
- Data archives: `FILEDATA.BIN`, `FILEDT02.BIN`, `FILEDT03.BIN`,
  `FILEDT04.BIN`, `SD.BIN`
- `SD.BIN` has a `TYOSD v-2.00` header and **203 indexed resources**.
- Starting at header offset `0x14`, each 8-byte entry contains a resource
  byte length and the next resource's starting 2048-byte sector.
- All 202 nonterminal SD index transitions match the sector alignment rule.
  The last next-sector field is `0xFFFFFFFF`.
- The first indexed resource starts `SdDt` and contains `sdtr` / `tvag`.
- `FILEDATA.BIN` starts `Svag`, and three `FILEDT*.BIN` files start with
  MPEG video data.
- `DATA00.BIN` through `DATA09.BIN` are `MWo3` program modules, *not*
  the resource directory.

## Planned porting work

1. Map the gameplay-song index in the large audio archive.
2. Identify Extreme 2 chart encoding and rendering formats.
3. Identify song metadata/difficulty records and image assets.
4. Reuse StepMania input conversion, transliteration, user interface, batch
   processing and ISO rebuild concepts from the tested DDR X version.
5. Validate actual ISO replacement in PCSX2.

**Do not run the DDR X writer on Extreme 2.** No Extreme 2 modified ISO has
been produced or tested yet.

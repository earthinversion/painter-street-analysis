# Sources and licenses

Original release code: MIT, copyright 2026 Utpal Kumar. Original documentation, figures, and derived analysis tables: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/legalcode). These licenses apply to the original contributions, not to third-party source metadata or underlying recordings.

Strong-motion source: California Geological Survey and U.S. Geological Survey (2005), *Center for Engineering Strong Motion Data (CESMD)*, [doi:10.5066/P13HTZQS](https://doi.org/10.5066/P13HTZQS). Records were provided by CGS/CSMIP through the Caltrans–CGS instrumentation program. Preserve provider attribution and consult the [CESMD data policy](https://www.strongmotioncenter.org/NCESMD/reports/CESMD_DataPolicy.htm) and the terms supplied with any new download. No waveform files are redistributed here. The original download requires a registered email; this offline example requires no account.

Inspection source: Federal Highway Administration (2025), *National Bridge Inventory*, California state files for 2012–2025, structure `04 0236`. Original URLs and checksums are retained in `data/inspection_sources.json`. Inspection values are source records, not newly measured quantities.

Method reference: Muin, S., Chern, C., and Mosalam, K. M. (2024). Human–Machine Collaboration Framework for Bridge Health Monitoring. *Journal of Bridge Engineering*, 29(7), 04024041. [doi:10.1061/JBENF2.BEENG-6587](https://doi.org/10.1061/JBENF2.BEENG-6587).

Upstream modal identification used Chrystal Chern’s `mdof` package (0.0.22, BSD-2-Clause) and a local implementation. No `mdof` source is included in this release. The Python dependencies retain their respective licenses.

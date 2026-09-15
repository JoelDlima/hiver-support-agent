---
title: Data Augmentation for Intent Classification with Off-the-shelf Large Language
  Models - ACL Anthology
id: data-augmentation-for-intent-classification-with-off-the-shelf-large-language-mo
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:30:31.444406Z'
source: https://aclanthology.org/2022.nlp4convai-1.5/
source_domain: aclanthology.org
fetched_at: '2026-09-15T02:30:31.442406Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
doi: 10.18653/v1/2022.nlp4convai-1.5
citation_count: 64
is_retracted: false
---

Data Augmentation for Intent Classification with Off-the-shelf Large Language Models - ACL Anthology
Data Augmentation for Intent Classification with Off-the-shelf Large Language Models
Gaurav Sahu
,
Pau Rodriguez
,
Issam Laradji
,
Parmida Atighehchian
,
David Vazquez
,
Dzmitry Bahdanau
Correct Metadata for
Use this form to create a GitHub issue with structured data describing the correction. You will need a GitHub account.
Once you create that issue, the correction will be reviewed by a staff member.
⚠️ Mobile Users: Submitting this form to create a new issue will only work with github.com, not the GitHub Mobile app.
Important
: The Anthology treat PDFs as authoritative. Please use this form only to correct data
that is out of line with the PDF. See
our corrections
guidelines
if you need to change the PDF.
Title
Adjust the title. Retain tags such as
<fixed-case>.
Authors
Adjust author names and order to match the
PDF.
Add Author
Abstract
Correct abstract if needed. Retain XML formatting tags such as <tex-math>. You may use <b>...</b> for
bold
, <i>...</i> for
italic
, <u>...</u> for
underline
, <sc>...</sc> for
small-caps
, <tt>...<tt> for
typewriter text
, <url>...</url> for URLs, <a href=...> for hyperlinks, and <par/> for paragraph breaks.
Verification against PDF
Ensure that the new title/authors match the snapshot below. (If there
is no snapshot or it is too small, consult
the PDF
.)
Authors concatenated from the text boxes above:
ALL author names match the snapshot above—including
middle initials, hyphens, and accents.
Create GitHub issue for staff review
Abstract
Data augmentation is a widely employed technique to alleviate the problem of data scarcity. In this work, we propose a prompting-based approach to generate labelled training data for intent classification with off-the-shelf language models (LMs) such as GPT-3. An advantage of this method is that no task-specific LM-fine-tuning for data generation is required; hence the method requires no hyper parameter tuning and is applicable even when the available training data is very scarce. We evaluate the proposed method in a few-shot setting on four diverse intent classification tasks. We find that GPT-generated data significantly boosts the performance of intent classifiers when intents in consideration are sufficiently distinct from each other. In tasks with semantically close intents, we observe that the generated data is less helpful. Our analysis shows that this is because GPT often generates utterances that belong to a closely-related intent instead of the desired one. We present preliminary evidence that a prompting-based GPT classifier could be helpful in filtering the generated data to enhance its quality.
Anthology ID:
2022.nlp4convai-1.5
Volume:
Proceedings of the 4th Workshop on NLP for Conversational AI
Month:
May
Year:
2022
Address:
Dublin, Ireland
Editors:
Bing Liu
,
Alexandros Papangelis
,
Stefan Ultes
,
Abhinav Rastogi
,
Yun-Nung Chen
,
Georgios Spithourakis
,
Elnaz Nouri
,
Weiyan Shi
Venues:
NLP4ConvAI
|
WS
SIG:
Publisher:
Association for Computational Linguistics
Note:
Pages:
47–57
Language:
URL:
https://aclanthology.org/2022.nlp4convai-1.5/
DOI:
10.18653/v1/2022.nlp4convai-1.5
Bibkey:
sahu-etal-2022-data
Cite (ACL):
Gaurav Sahu, Pau Rodriguez, Issam Laradji, Parmida Atighehchian, David Vazquez, and Dzmitry Bahdanau. 2022.
Data Augmentation for Intent Classification with Off-the-shelf Large Language Models
. In
Proceedings of the 4th Workshop on NLP for Conversational AI
, pages 47–57, Dublin, Ireland. Association for Computational Linguistics.
Cite (Informal):
Data Augmentation for Intent Classification with Off-the-shelf Large Language Models
(Sahu et al., NLP4ConvAI 2022)
Copy Citation:
BibTeX
Markdown
MODS XML
Endnote
More
options…
PDF:
https://aclanthology.org/2022.nlp4convai-1.5.pdf
Video:
https://aclanthology.org/2022.nlp4convai-1.5.mp4
PDF
Cite
Search
Video
Fix data
Export citation
BibTeX
MODS XML
Endnote
Preformatted
@inproceedings{sahu-etal-2022-data,
    title = "Data Augmentation for Intent Classification with Off-the-shelf Large Language Models",
    author = "Sahu, Gaurav  and
      Rodriguez, Pau  and
      Laradji, Issam  and
      Atighehchian, Parmida  and
      Vazquez, David  and
      Bahdanau, Dzmitry",
    editor = "Liu, Bing  and
      Papangelis, Alexandros  and
      Ultes, Stefan  and
      Rastogi, Abhinav  and
      Chen, Yun-Nung  and
      Spithourakis, Georgios  and
      Nouri, Elnaz  and
      Shi, Weiyan",
    booktitle = "Proceedings of the 4th Workshop on NLP for Conversational AI",
    month = may,
    year = "2022",
    address = "Dublin, Ireland",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.nlp4convai-1.5/",
    doi = "10.18653/v1/2022.nlp4convai-1.5",
    pages = "47--57",
    abstract = "Data augmentation is a widely employed technique to alleviate the problem of data scarcity. In this work, we propose a prompting-based approach to generate labelled training data for intent classification with off-the-shelf language models (LMs) such as GPT-3. An advantage of this method is that no task-specific LM-fine-tuning for data generation is required; hence the method requires no hyper parameter tuning and is applicable even when the available training data is very scarce. We evaluate the proposed method in a few-shot setting on four diverse intent classification tasks. We find that GPT-generated data significantly boosts the performance of intent classifiers when intents in consideration are sufficiently distinct from each other. In tasks with semantically close intents, we observe that the generated data is less helpful. Our analysis shows that this is because GPT often generates utterances that belong to a closely-related intent instead of the desired one. We present preliminary evidence that a prompting-based GPT classifier could be helpful in filtering the generated data to enhance its quality."
}
Download as
File
Copy to Clipboard
<?xml version="1.0" encoding="UTF-8"?>
<modsCollection xmlns="http://www.loc.gov/mods/v3">
<mods ID="sahu-etal-2022-data">
    <titleInfo>
        <title>Data Augmentation for Intent Classification with Off-the-shelf Large Language Models</title>
    </titleInfo>
    <name type="personal">
        <namePart type="given">Gaurav</namePart>
        <namePart type="family">Sahu</namePart>
        <role>
            <roleTerm authority="marcrelator" type="text">author</roleTerm>
        </role>
    </name>
    <name type="personal">
        <namePart type="given">Pau</namePart>
        <namePart type="family">Rodriguez</namePart>
        <role>
            <roleTerm authority="marcrelator" type="text">author</roleTerm>
        </role>
    </name>
    <name type="personal">
        <namePart type="given">Issam</namePart>
        <namePart type="family">Laradji</namePart>
        <role>
            <roleTerm authority="marcrelator" type="text">author</roleTerm>
        </role>
    </name>
    <name type="personal">
        <namePart type="given">Parmida</namePart>
        <namePart type="family">Atighehchian</namePart>
        <role>
            <roleTerm authority="marcrelator" type="text">author</roleTerm>
        </role>
    </name>
    <name type="personal">
        <namePart type="given">David</namePart>
        <namePart type="family">Vazquez</namePart>
        <role>
            <roleTerm authority="marcrelator" type="text">author</roleTerm>
        </role>
    </name>
    <name type="personal">
        <namePart type="given">Dzmitry</namePart>
        <namePart type="family">Bahdanau</namePart>
        <role>
            <roleTerm authority="marcrelator" type="text">author</roleTerm>
        </role>
    </name>
    <originInfo>
        <dateIssued>2022-05</dateIssued>
    </originInfo>
    <typeOfResource>text</typeOfResource>
    <relatedItem type="host">
        <titleInfo>
            <title>Proceedings of the 4th Workshop on NLP for Conversational AI</title>
        </titleInfo>
        <name type="personal">
            <namePart type="given">Bing</namePart>
            <namePart type="family">Liu</namePart>
            <role>
                <roleTerm authority="marcrelator" type="text">editor</roleTerm>
            </role>
        </name>
        <name type="personal">
            <namePart type="given">Alexandros</namePart>
            <namePart type="family">Papangelis</namePart>
            <role>
                <roleTerm authority="marcrelator" type="text">editor</roleTerm>
            </role>
        </name>
        <name type="personal">
            <namePart type="given">Stefan</namePart>
            <namePart type="family">Ultes</namePart>
            <role>
                <roleTerm authority="marcrelator" type="text">editor</roleTerm>
            </role>
        </name>
        <name type="personal">
            <namePart type="given">Abhinav</namePart>
            <namePart type="family">Rastogi</namePart>
            <role>
                <roleTerm authority="marcrelator" type="text">editor</roleTerm>
            </role>
        </name>
        <name type="personal">
            <namePart type="given">Yun-Nung</namePart>
            <namePart type="family">Chen</namePart>
            <role>
                <roleTerm authority="marcrelator" type="text">editor</roleTerm>
            </role>
        </name>
        <name type="personal">
            <namePart type="given">Georgios</namePart>
            <namePart type="family">Spithourakis</namePart>
            <role>
                <roleTerm authority="marcrelator" type="text">editor</roleTerm>
            </role>
        </name>
        <name type="personal">
            <namePart type="given">Elnaz</namePart>
            <namePart type="family">Nouri</namePart>
            <role>
                <roleTerm authority="marcrelator" type="text">editor</roleTerm>
            </role>
        </name>
        <name type="personal">
            <namePart type="given">Weiyan</namePart>
            <namePart type="family">Shi</namePart>
            <role>
                <roleTerm authority="marcrelator" type="text">editor</roleTerm>
            </role>
        </name>
        <originInfo>
            <publisher>Association for Computational Linguistics</publisher>
            <place>
                <placeTerm type="text">Dublin, Ireland</placeTerm>
            </place>
        </originInfo>
        <genre authority="marcgt">conference publication</genre>
    </relatedItem>
    <abstract>Data augmentation is a widely employed technique to alleviate the problem of data scarcity. In this work, we propose a prompting-based approach to generate labelled training data for intent classification with off-the-shelf language models (LMs) such as GPT-3. An advantage of this method is that no task-specific LM-fine-tuning for data generation is required; hence the method requires no hyper parameter tuning and is applicable even when the available training data is very scarce. We evaluate the proposed method in a few-shot setting on four diverse intent classification tasks. We find that GPT-generated data significantly boosts the performance of intent classifiers when intents in consideration are sufficiently distinct from each other. In tasks with semantically close intents, we observe that the generated data is less helpful. Our analysis shows that this is because GPT often generates utterances that belong to a closely-related intent instead of the desired one. We present preliminary evidence that a prompting-based GPT classifier could be helpful in filtering the generated data to enhance its quality.</abstract>
    <identifier type="citekey">sahu-etal-2022-data</identifier>
    <identifier type="doi">10.18653/v1/2022.nlp4convai-1.5</identifier>
    <location>
        <url>https://aclanthology.org/2022.nlp4convai-1.5/</url>
    </location>
    <part>
        <date>2022-05</date>
        <extent unit="page">
            <start>47</start>
            <end>57</end>
        </extent>
    </part>
</mods>
</modsCollection>
Download as
File
Copy to Clipboard
%0 Conference Proceedings
%T Data Augmentation for Intent Classification with Off-the-shelf Large Language Models
%A Sahu, Gaurav
%A Rodriguez, Pau
%A Laradji, Issam
%A Atighehchian, Parmida
%A Vazquez, David
%A Bahdanau, Dzmitry
%Y Liu, Bing
%Y Papangelis, Alexandros
%Y Ultes, Stefan
%Y Rastogi, Abhinav
%Y Chen, Yun-Nung
%Y Spithourakis, Georgios
%Y Nouri, Elnaz
%Y Shi, Weiyan
%S Proceedings of the 4th Workshop on NLP for Conversational AI
%D 2022
%8 May
%I Association for Computational Linguistics
%C Dublin, Ireland
%F sahu-etal-2022-data
%X Data augmentation is a widely employed technique to alleviate the problem of data scarcity. In this work, we propose a prompting-based approach to generate labelled training data for intent classification with off-the-shelf language models (LMs) such as GPT-3. An advantage of this method is that no task-specific LM-fine-tuning for data generation is required; hence the method requires no hyper parameter tuning and is applicable even when the available training data is very scarce. We evaluate the proposed method in a few-shot setting on four diverse intent classification tasks. We find that GPT-generated data significantly boosts the performance of intent classifiers when intents in consideration are sufficiently distinct from each other. In tasks with semantically close intents, we observe that the generated data is less helpful. Our analysis shows that this is because GPT often generates utterances that belong to a closely-related intent instead of the desired one. We present preliminary evidence that a prompting-based GPT classifier could be helpful in filtering the generated data to enhance its quality.
%R 10.18653/v1/2022.nlp4convai-1.5
%U https://aclanthology.org/2022.nlp4convai-1.5/
%U https://doi.org/10.18653/v1/2022.nlp4convai-1.5
%P 47-57
Download as
File
Copy to Clipboard
Markdown (Informal)
[Data Augmentation for Intent Classification with Off-the-shelf Large Language Models](https://aclanthology.org/2022.nlp4convai-1.5/) (Sahu et al., NLP4ConvAI 2022)
Data Augmentation for Intent Classification with Off-the-shelf Large Language Models
(Sahu et al., NLP4ConvAI 2022)
ACL
Gaurav Sahu, Pau Rodriguez, Issam Laradji, Parmida Atighehchian, David Vazquez, and Dzmitry Bahdanau. 2022.
Data Augmentation for Intent Classification with Off-the-shelf Large Language Models
. In
Proceedings of the 4th Workshop on NLP for Conversational AI
, pages 47–57, Dublin, Ireland. Association for Computational Linguistics.
Copy Markdown to
Clipboard
Copy ACL to
Clipboard
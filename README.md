# Item7-readability
this repository contains code for calculating the readability of "Management’s Discussion and Analysis of Financial Condition and Results of Operations" from the annual report

Overview

This repository contains code for calculating the readability of the "Management’s Discussion and Analysis of Financial Condition and Results of Operations" (Item 7) from annual reports.

Employing Item 7 of the 10-K reports over a 26-year period, this study examines the evolving readability of financial reporting. Using a dataset of more than 200,000 reports retrieved from SEC EDGAR filings, we observe a noticeable decline in readability over time.

Key Findings

Using the Fog Index as a readability measure, we find that the number of years of schooling required to comprehend Item 7 has increased steadily. Specifically:

In 1996, the average Fog Index score for Item 7 was 17.6.

By 2022, the score had increased to 20.19.

This equates to an average annual increase of 0.09 points, meaning each year, the required reading level grows by approximately one additional month of education.

This trend suggests that financial reports are becoming increasingly inaccessible to a significant portion of the population, potentially hindering effective communication between corporations and investors.

Comparative Analysis

To contextualize these findings, we analyze financial text complexity across multiple corpora, totaling nearly 10 million documents. A key exception to the observed trend is the Wall Street Journal, which does not exhibit a significant increase in complexity over time and may even show a slight decline.

The following figure illustrates the core findings, visualizing the temporal evolution of the Fog Index across different corpora, including a regression-fitted line with confidence intervals and p-values to quantify statistical significance.

Data Availability

While we provide code and methodologies, access to certain datasets is restricted due to licensing and subscription constraints:

Item 7 (10-K Reports): Available for download from Zenodo.

Credit Card Agreement Database: Freely available at the Consumer Financial Protection Bureau.

The Telegraph Newspaper Corpus as well as the WSJ: Not available, as it is no longer free.

Academic Articles: Not included, as they were obtained through institutional subscriptions and cannot be shared publicly. 


![image](https://github.com/dannylesmy/Item7-readability/assets/63964315/3c4a4af1-446d-4937-958f-090bb742b569)


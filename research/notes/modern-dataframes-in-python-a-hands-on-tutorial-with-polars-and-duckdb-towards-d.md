---
title: 'Modern DataFrames in Python: A Hands-On Tutorial with Polars and DuckDB |
  Towards Data Science'
id: modern-dataframes-in-python-a-hands-on-tutorial-with-polars-and-duckdb-towards-d
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:17.004242Z'
source: https://towardsdatascience.com/modern-dataframes-in-python-a-hands-on-tutorial-with-polars-and-duckdb/
source_domain: towardsdatascience.com
fetched_at: '2026-09-15T02:28:17.002248Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Modern DataFrames in Python: A Hands-On Tutorial with Polars and DuckDB | Towards Data Science
If you have worked with Python for data, you have probably experienced the frustration of waiting minutes for a Pandas operation to finish.
At first, everything seems fine, but as your dataset grows and your workflows become more complex, your laptop suddenly feels like it's preparing for lift-off.
A couple of months ago, I worked on a project analyzing e-commerce transactions with over 3 million rows of data.
It was a pretty interesting experience, but most of the time, I watched simple groupby operations that normally ran in seconds suddenly stretch into minutes.
At that point, I realized Pandas is amazing, but it is not always enough.
This article explores modern alternatives to Pandas, including Polars and DuckDB, and examines how they can simplify and improve the handling of large datasets.
For clarity, let me be upfront about a few things before we begin.
This article is not a deep dive into Rust memory management or a proclamation that Pandas is obsolete.
Instead, it is a practical, hands-on guide. You will see real examples, personal experiences, and actionable insights into workflows that can save you time and sanity.
···
Why Pandas Can Feel Slow
Back when I was on the e-commerce project, I remember working with CSV files over two gigabytes, and every filter or aggregation in Pandas often took several minutes to complete.
During that time, I would stare at the screen, wishing I could just grab a coffee or binge a few episodes of a show while the code ran.
The main pain points I encountered were speed, memory, and workflow complexity.
We all know how large CSV files consume enormous amounts of RAM, sometimes more than what my laptop could comfortably handle. On top of that, chaining multiple transformations also made code harder to maintain and slower to execute.
Polars and DuckDB address these challenges in different ways.
Polars, built in Rust, uses multi-threaded execution to process large datasets efficiently.
DuckDB, on the other hand, is designed for analytics and executes SQL queries without needing you to load everything into memory.
Basically, each of them has its own superpower. Polars is the speedster, and DuckDB is kind of like the memory magician.
And the best part? Both integrate seamlessly with Python, allowing you to enhance your workflows without a complete rewrite.
Setting Up Your Environment
Before we start coding, make sure your environment is ready. For consistency, I used Pandas 2.2.0, Polars 0.20.0, and DuckDB 1.9.0.
Pinning versions can save you headaches when following tutorials or sharing code.
bash
pip install pandas==2.2.0 polars==0.20.0 duckdb==1.9.0
In Python, import the libraries:
python
import pandas as pd
import polars as pl
import duckdb
import warnings
warnings.filterwarnings("ignore")
For example, I will use an e-commerce sales dataset with columns such as order ID, product ID, region, country, revenue, and date. You can download similar datasets from
Kaggle
or generate synthetic data.
Loading Data
Loading data efficiently sets the tone for the rest of your workflow. I remember a project where the CSV file had nearly 5 million rows.
Pandas handled it, but the load times were long, and the repeated reloads during testing were painful.
It was one of those moments where you wish your laptop had a “fast forward” button.
Switching to Polars and DuckDB completely improved everything, and suddenly, I could access and manipulate the data almost instantly, which honestly made the testing and iteration processes far more enjoyable.
With Pandas:
python
df_pd = pd.read_csv("sales.csv")
print(df_pd.head(3))
With Polars:
python
df_pl = pl.read_csv("sales.csv")
print(df_pl.head(3))
With DuckDB:
python
con = duckdb.connect()
df_duck = con.execute("SELECT * FROM 'sales.csv'").df()
print(df_duck.head(3))
DuckDB can query CSVs directly without loading the entire datasets into memory, making it much easier to work with large files.
Filtering Data
The problem here is that filtering in Pandas can be slow when dealing with millions of rows. I once needed to analyze European transactions in a massive sales dataset. Pandas took minutes, which slowed down my analysis.
With Pandas:
python
filtered_pd = df_pd[df_pd.region == "Europe"]
Polars is faster and can process multiple filters efficiently:
python
filtered_pl = df_pl.filter(pl.col("region") == "Europe")
DuckDB uses SQL syntax:
python
filtered_duck = con.execute("""
SELECT *
FROM 'sales.csv'
WHERE region = 'Europe'
""").df()
Now you can filter through large datasets in seconds instead of minutes, leaving you more time to focus on the insights that really matter.
Aggregating Large Datasets Quickly
Aggregation is often where Pandas starts to feel slow. Imagine calculating total revenue per country for a marketing report.
In Pandas:
python
agg_pd = df_pd.groupby("country")["revenue"].sum().reset_index()
In Polars:
python
agg_pl = df_pl.groupby("country").agg(pl.col("revenue").sum())
In DuckDB:
python
agg_duck = con.execute("""
SELECT country, SUM(revenue) AS total_revenue
FROM 'sales.csv'
GROUP BY country
""").df()
I remember running this aggregation on a 10 million-row dataset. In Pandas, it took nearly half an hour. Polars completed the same operation in under a minute.
The sense of relief was almost like finishing a marathon and realizing your legs still work.
Joining Datasets at Scale
Joining datasets is one of those things that sounds simple until you are actually knee-deep in the data.
In real projects, your data usually lives in multiple sources, so you have to combine them using shared columns like customer IDs.
I learned this the hard way while working on a project that required combining millions of customer orders with an equally large demographic dataset.
Each file was big enough on its own, but merging them felt like trying to force two puzzle pieces together while your laptop begged for mercy.
Pandas took so long that I began timing the joins the same way people time how long it takes their microwave popcorn to finish.
Spoiler: the popcorn won every time.
Polars and DuckDB gave me a way out.
With Pandas:
python
merged_pd = df_pd.merge(pop_df_pd, on="country", how="left")
Polars:
python
merged_pl = df_pl.join(pop_df_pl, on="country", how="left")
DuckDB:
python
merged_duck = con.execute("""
SELECT *
FROM 'sales.csv' s
LEFT JOIN 'pop.csv' p
USING (country)
""").df()
Joins
on large datasets that used to freeze your workflow now run smoothly and efficiently.
Lazy Evaluation in Polars
One thing I didn’t appreciate early in my data science journey was how much time gets wasted while running transformations line by line.
Polars approaches this differently.
It uses a technique called lazy evaluation, which essentially waits until you have completed defining your transformations before executing any operations.
It examines the entire pipeline, determines the most efficient path, and executes everything simultaneously.
It’s like having a friend who listens to your entire order before walking to the kitchen, instead of one who takes each instruction separately and keeps going back and forth.
This
TDS article
indepthly explains lazy evaluation.
Here’s what the flow looks like:
Pandas:
python
df = df[df["amount"] > 100]
df = df.groupby("segment").agg({"amount": "mean"})
df = df.sort_values("amount")
Polars Lazy Mode:
python
import polars as pl
df_lazy = (
pl.scan_csv("sales.csv")
.filter(pl.col("amount") > 100)
.groupby("segment")
.agg(pl.col("amount").mean())
.sort("amount")
)
result = df_lazy.collect()
The first time I used lazy mode, it felt strange not seeing instant results. But once I ran the final
.collect()
, the speed difference was obvious.
Lazy evaluation won’t magically solve every performance issue, but it brings a level of efficiency that Pandas wasn’t designed for.
···
Conclusion and takeaways
Working with large datasets doesn’t have to feel like wrestling with your tools.
Using Polars and DuckDB showed me that the problem wasn’t always the data. Sometimes, it was the tool I was using to handle it.
If there is one thing you take away from this tutorial, let it be this: you don’t have to abandon Pandas, but you can reach for something better when your datasets start pushing their limits.
Polars gives you speed as well as smarter execution, then DuckDB lets you query huge files like they’re tiny. Together, they make working with large data feel more manageable and less tiring.
If you want to go deeper into the ideas explored in this tutorial, the official documentation of
Polars
and
DuckDB
are good places to start.
Related Articles
Purist v Pragmatist - why we can both agree on automation
Programming
We all strive for solutions that are sustainable yet we sit on spaghetti code, with our future inevitable ... spaghetti code in the cloud.
Corné Potgieter
November 29, 2021
6 min read
Simple and multiple linear regression with Python
Machine Learning
Linear regression is a linear approach to model the relationship between a dependent variable (target variable) and one (simple...
Amanda Iglesias Moreno
July 27, 2019
11 min read
The Battle of Interactive Geographic Visualization Part 4 - Altair
Data Science
Using the Altair Package to Create Beautiful, Interactive Geoplots
TheDataProf
March 8, 2022
5 min read
SQL to SARIMAX: How I navigate the first time-series analysis personal project for my portfolio
Data Science
Including the resources I used to learn time-series as I was doing this project (MySQL, ARIMA orders selection, parallelization in Jupyter...
Irene Chang
April 6, 2022
10 min read
AI Coding: Is Google Bard a Good Python Developer?
Artificial Intelligence
How does Google Bard handle Python coding tasks?
Marcin Kozak
November 9, 2023
20 min read
Data preparation with klib
Data Science
Fast and simple function calls for efficient data preparation
Andreas Kanz
December 5, 2020
4 min read
How to Upgrade Your Junior-Level Data Science Code to Senior-Level Data Science Code
Artificial Intelligence
These 4 tips will have you writing code like a senior data scientist
Madison Hunter
June 12, 2023
7 min read
Forecasting with Stochastic Models
Artificial Intelligence
Using ARIMA models to Forecast Walmart Sales data
Kurtis Pykes
June 12, 2020
10 min read
How to Speed up Python Data Pipelines up to 91X?
Programming
A 5-minute tutorial that could save months of your big-data projects.
Thuwarakesh Murallie
July 18, 2021
6 min read
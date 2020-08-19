
<br>
<br>

<p style="text-align:center">
    <img width=50% src="docs/source/images/compose.png" alt="Compose" />
</p>

<br>
<br>

[![CircleCI](https://circleci.com/gh/FeatureLabs/compose/tree/main.svg?)](https://circleci.com/gh/FeatureLabs/compose/tree/main)
[![codecov](https://codecov.io/gh/FeatureLabs/compose/branch/main/graph/badge.svg)](https://codecov.io/gh/FeatureLabs/compose)
[![Documentation Status](https://readthedocs.com/projects/feature-labs-inc-compose/badge/?version=stable&token=5c3ace685cdb6e10eb67828a4dc74d09b20bb842980c8ee9eb4e9ed168d05b00)](https://compose.alteryx.com/en/stable/?badge=stable)
[![PyPI version](https://badge.fury.io/py/composeml.svg?maxAge=2592000)](https://badge.fury.io/py/composeml)
[![StackOverflow](https://img.shields.io/badge/questions-on_stackoverflow-blue.svg)](https://stackoverflow.com/questions/tagged/composeml)
[![Downloads](https://pepy.tech/badge/composeml/month)](https://pepy.tech/project/composeml/month)

[Compose](https://compose.alteryx.com) is a python library for automated prediction engineering. An end user defines an outcome of interest over the data by writing a "labeling function". Compose will automatically search and extract historical training examples to train machine learning examples, balance them across time, entities and label categories to reduce biases in learning process. See the [documentation](https://compose.alteryx.com) for more information.

Its result is then provided to the automatic feature engineering tools Featuretools and subsequently to AutoML/ML libraries to develop a model. This automation for the very early stage of ML pipeline process allows our end user to easily define a task and solve it. The workflow of an applied machine learning engineer then becomes:

<br>
<p align="center">
    <img width=90% src="docs/source/images/workflow.png" alt="Compose" />
</p>
<br>

## Install

Compose can be installed with Python 3.6 or later by running the following command:

```
pip install composeml
```

## Example

> Will a customer spend more than 300 in the next hour of transactions?

In this example, we automatically generate new training examples from a historical dataset of transactions.


```python
import composeml as cp
df = cp.demos.load_transactions()
df = df[df.columns[:7]]
df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>transaction_id</th>
      <th>session_id</th>
      <th>transaction_time</th>
      <th>product_id</th>
      <th>amount</th>
      <th>customer_id</th>
      <th>device</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>298</td>
      <td>1</td>
      <td>2014-01-01 00:00:00</td>
      <td>5</td>
      <td>127.64</td>
      <td>2</td>
      <td>desktop</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10</td>
      <td>1</td>
      <td>2014-01-01 00:09:45</td>
      <td>5</td>
      <td>57.39</td>
      <td>2</td>
      <td>desktop</td>
    </tr>
    <tr>
      <th>2</th>
      <td>495</td>
      <td>1</td>
      <td>2014-01-01 00:14:05</td>
      <td>5</td>
      <td>69.45</td>
      <td>2</td>
      <td>desktop</td>
    </tr>
    <tr>
      <th>3</th>
      <td>460</td>
      <td>10</td>
      <td>2014-01-01 02:33:50</td>
      <td>5</td>
      <td>123.19</td>
      <td>2</td>
      <td>tablet</td>
    </tr>
    <tr>
      <th>4</th>
      <td>302</td>
      <td>10</td>
      <td>2014-01-01 02:37:05</td>
      <td>5</td>
      <td>64.47</td>
      <td>2</td>
      <td>tablet</td>
    </tr>
  </tbody>
</table>
</div>



First, we represent the prediction problem with a labeling function and a label maker.


```python
def total_spent(ds):
    return ds['amount'].sum()

label_maker = cp.LabelMaker(
    target_entity="customer_id",
    time_index="transaction_time",
    labeling_function=total_spent,
    window_size="1h",
)
```

Then, we run a search to automatically generate the training examples.


```python
label_times = label_maker.search(
    df.sort_values('transaction_time'),
    num_examples_per_instance=2,
    minimum_data='2014-01-01',
    drop_empty=False,
    verbose=False,
)

label_times = label_times.threshold(300)
label_times.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>customer_id</th>
      <th>time</th>
      <th>total_spent</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2014-01-01 00:00:00</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>2014-01-01 01:00:00</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>2014-01-01 00:00:00</td>
      <td>False</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2</td>
      <td>2014-01-01 01:00:00</td>
      <td>False</td>
    </tr>
    <tr>
      <th>4</th>
      <td>3</td>
      <td>2014-01-01 00:00:00</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>



These labels are now ready for building features with Featuretools and training machine learning models with EvalML.

## Testing & Development
The Feature Labs community welcomes pull requests. Instructions for testing and development are available here.

## Support
The Feature Labs open source community is happy to provide support to users of Compose. Project support can be found in four places depending on the type of question:

1. For usage questions, use [Stack Overflow](https://stackoverflow.com/questions/tagged/composeml) with the `composeml` tag.
2. For bugs, issues, or feature requests start a Github [issue](https://github.com/FeatureLabs/compose/issues).
3. For discussion regarding development on the core library, use [Slack](https://featuretools.slack.com/messages/CKP6D0KUP).
4. For everything else, the core developers can be reached by email at [help@featurelabs.com](mailto:help@featurelabs.com).

## Citing Compose
Compose is built upon a newly defined part of the machine learning process - prediction engineering. If you use Compose please consider citing this paper:
James Max Kanter, Gillespie, Owen, Kalyan Veeramachaneni. [Label, Segment,Featurize: a cross domain framework for prediction engineering.](https://dai.lids.mit.edu/wp-content/uploads/2017/10/Pred_eng1.pdf) IEEE DSAA 2016.

BibTeX entry:

```
@inproceedings{kanter2016label,
  title={Label, segment, featurize: a cross domain framework for prediction engineering},
  author={Kanter, James Max and Gillespie, Owen and Veeramachaneni, Kalyan},
  booktitle={2016 IEEE International Conference on Data Science and Advanced Analytics (DSAA)},
  pages={430--439},
  year={2016},
  organization={IEEE}
}
```

## Acknowledgements 
Compose open source has been developed by Feature Labs engineering team. The open source development has been supported in part by DARPA's Data driven discovery of models program (D3M). 

## Feature Labs
<a href="https://www.featurelabs.com/">
    <img src="https://www.featurelabs.com/wp-content/uploads/2017/12/logo.png" alt="Featuretools" />
</a>

Compose is an open source project created by Feature Labs. We developed Compose to enable flexible definition of the machine learning task. Read more about our rationale behind automating and developing this stage of the machine learning process here.

To see the other open source projects we're working on visit Feature Labs [Open Source](https://www.featurelabs.com/open). If building impactful data science pipelines is important to you or your business, please [get in touch](https://www.featurelabs.com/contact/).

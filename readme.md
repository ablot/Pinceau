# Model of the pinceau

Model used in [Ultra-rapid axon-axon ephaptic inhibition of cerebellar Purkinje 
cells by the pinceau](https://www.nature.com/articles/nn.3624).

## Dependencies

The code is a bit outdated. It should run with python 2.7 and ipython 3.2.1. If you 
use conda, this should work:

```
conda create -n pinceau python=2.7
source activate pinceau
conda install matplotlib numpy twisted scipy
conda install ipython=3.2.1
 
```

## Running the code

To run the parent folder of `Pinceau` must be in the path. Assuming the repository
was cloned in `/home/user/code/Pinceau`, I usually just do:

```
>>> source activate pinceau
>>> ipython

In[1]: cd /home/user/code/
In[2]: %run Pinceau/model/'script you want to run'
```

## Regenerating the figures

### Figure 4

Running `plot_vqrious_freq_CC.py` should regenerate everything (see flags at the
beginning of the file if it doesn't). To be more precise 3 functions are called:
- Panels **b-e** are generated by `doCtrlPlot()` and saved in `ctrl_example_Vpurk.svg`
- Panel  **f** is generated by `doKPlot()` and saved in `ctrl_example_CtNoKNoC_BA.svg`
- Panel **h**  is generated by `doCrossCorrPlot()` and saved in `.svg`

### Supplementary figure 2 (Basket effect)

Run `basket_effect.py`. It should generate `figSuppBasket.pdf` (panels a-f) 
and `model_cc_basketonly.pdf` (panel g).
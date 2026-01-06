use pyo3::prelude::*;

/// Tiny example function to validate the Rust/Python fallback wiring.
///
/// Real accelerated functions should keep behavior identical to the Python baseline.
#[pyfunction]
fn add_i64(a: i64, b: i64) -> i64 {
    a + b
}

#[pyfunction]
fn subset_list_stats(
    best_params: Vec<f64>,
    best_lnl: Vec<f64>,
    subset_sizes: Vec<usize>,
    num_taxa: usize,
    branchlengths: &str,
) -> PyResult<(f64, i64, i64)> {
    if best_params.len() != best_lnl.len() || best_params.len() != subset_sizes.len() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "best_params, best_lnl, subset_sizes must have same length",
        ));
    }

    let mut lnL: f64 = 0.0;
    let mut sum_subset_k: f64 = 0.0;
    let mut subs_len: i64 = 0;

    for ((k, lnl), nsites) in best_params
        .iter()
        .zip(best_lnl.iter())
        .zip(subset_sizes.iter())
    {
        sum_subset_k += *k;
        lnL += *lnl;
        subs_len += *nsites as i64;
    }

    let nt = num_taxa as i64;
    let sum_k: i64 = match branchlengths {
        "linked" => (sum_subset_k + ((best_params.len() as f64) - 1.0) + ((2 * nt) - 3) as f64) as i64,
        "unlinked" => (sum_subset_k + ((best_params.len() as f64) * ((2 * nt) - 3) as f64)) as i64,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Unknown branchlengths (expected 'linked' or 'unlinked')",
            ))
        }
    };

    Ok((lnL, sum_k, subs_len))
}

#[pyfunction]
fn subset_list_score(
    best_params: Vec<f64>,
    best_lnl: Vec<f64>,
    subset_sizes: Vec<usize>,
    num_taxa: usize,
    branchlengths: &str,
    model_selection: &str,
) -> PyResult<f64> {
    let (lnl, sum_k_i, subs_len_i) = subset_list_stats(best_params, best_lnl, subset_sizes, num_taxa, branchlengths)?;
    let sum_k = sum_k_i as f64;
    let mut n = subs_len_i as f64;

    let ms = model_selection.to_ascii_lowercase();
    match ms.as_str() {
        "aic" => Ok((-2.0 * lnl) + (2.0 * sum_k)),
        "aicc" => {
            if n < (sum_k + 2.0) {
                n = sum_k + 2.0;
            }
            Ok((-2.0 * lnl) + ((2.0 * sum_k) * (n / (n - sum_k - 1.0))))
        }
        "bic" => Ok((-2.0 * lnl) + (sum_k * n.ln())),
        _ => Err(pyo3::exceptions::PyValueError::new_err(
            "Unknown model_selection (expected 'aic', 'aicc', or 'bic')",
        )),
    }
}

#[pymodule]
fn _pf_accel(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add_i64, m)?)?;
    m.add_function(wrap_pyfunction!(subset_list_stats, m)?)?;
    m.add_function(wrap_pyfunction!(subset_list_score, m)?)?;
    Ok(())
}

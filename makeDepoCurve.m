% Inputs:
%   ts: array of size N containing times to settlement in years
%   dfs: array of size N discount factors
% Output:
%   curve: a struct containing data needed by getRateIntegral
function curve = makeDepoCurve(ts, dfs)

    % 1. Force inputs to be column vectors (prevents dimension errors later)
    ts = ts(:);
    dfs = dfs(:);

    if isempty(ts) || isempty(dfs)
        error('makeDepoCurve:EmptyInput. ts and dfs must be non-empty vectors.');
    end
    if numel(ts) ~= numel(dfs)
        error('makeDepoCurve:SizeMismatch. ts and dfs must have the same number of elements.');
    end
    if any(~isfinite(ts)) || any(ts <= 0)
        error('makeDepoCurve:InvalidTimes. ts must contain finite strictly positive times.');
    end
    if any(diff(ts) <= 0)
        error('makeDepoCurve:InvalidTimes. ts must be strictly increasing.');
    end
    if any(~isfinite(dfs)) || any(dfs <= 0)
        error('makeDepoCurve:InvalidDiscountFactors. dfs must contain finite strictly positive discount factors.');
    end

    % 2. Add the starting point (Time = 0, Discount Factor = 1)
    t_padded = [0; ts];
    df_padded = [1; dfs];

    % 3. Calculate the time steps between each tenor
    dt = diff(t_padded);

    % 4. Bootstrap the local interest rates for each interval
    % The math: r = -[ln(DF_i) - ln(DF_{i-1})] / dt
    local_rates = -diff(log(df_padded)) ./ dt;

    % 5. Pack everything neatly into the 'curve' struct
    curve.ts = ts;
    curve.dfs = dfs;
    curve.rates = local_rates; 
    
    % Cache the cumulative integral exactly at the given tenors to speed up the next function
    curve.cumInt = -log(dfs);  
    
    % Store the final rate specifically to handle the extrapolation rule
    curve.tailRate = local_rates(end); 

end
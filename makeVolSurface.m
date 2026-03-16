% Inputs:
%   fwdCurve: forward curve data
%   Ts: vector of expiry times
%   cps: vetor of 1 for call, -1 for put
%   deltas: vector of delta in absolute value (e.g. 0.25)
%   vols: matrix of volatilities
% Output:
%   surface: a struct containing data needed in getVol
function volSurf = makeVolSurface(fwdCurve, Ts, cps, deltas, vols)

    nT = numel(Ts);
    nM = numel(deltas);

    if nT < 1
        error('makeVolSurface:EmptyTenors', 'Ts must be non-empty.');
    end
    if numel(cps) ~= nM
        error('makeVolSurface:SizeMismatch. cps and deltas must have the same length.');
    end
    if any(~isfinite(Ts)) || any(Ts <= 0)
        error('makeVolSurface:InvalidTenors. Ts must contain finite strictly positive tenors.');
    end
    if any(diff(sort(Ts)) <= 0)
        error('makeVolSurface:InvalidTenors. Ts must be strictly increasing, up to sorting.');
    end
    if any(~isfinite(cps)) || any(cps ~= 1 & cps ~= -1)
        error('makeVolSurface:InvalidOptionType. cps must contain only +1 for calls or -1 for puts.');
    end
    if any(~isfinite(deltas)) || any(deltas <= 0 | deltas >= 1)
        error('makeVolSurface:InvalidDelta. deltas must contain only values strictly between 0 and 1.');
    end
    if ~(isnumeric(vols) && isreal(vols) && ~isempty(vols))
        error('makeVolSurface:InvalidVolatilityMatrix. vols must be a non-empty real numeric matrix.');
    end

    num_tenors = length(Ts);
    smiles = cell(num_tenors, 1);
    fwds = zeros(num_tenors, 1);
    atm_vars = zeros(num_tenors, 1); 

    for i = 1:num_tenors
        T = Ts(i);
        vol_row = vols(i, :);
        
        fwd = getFwdSpot(fwdCurve, T);
        fwds(i) = fwd;
        
        % CRITICAL FIX: This now correctly passes fwdCurve and matches the new input order!
        sm = makeSmile(fwdCurve, T, cps, deltas, vol_row);
        smiles{i} = sm;
        
        % No-Arbitrage Check
        atm_vol = getSmileVol(sm, fwd);
        atm_vars(i) = (atm_vol^2) * T;
        
        if i > 1
            assert(atm_vars(i) >= atm_vars(i-1), ...
                sprintf('Calendar Arbitrage Violation at Tenor %d (Variance decreased!)', i));
        end
    end

    volSurf.fwdCurve = fwdCurve;
    volSurf.Ts = Ts(:);
    volSurf.smiles = smiles;
    volSurf.fwds = fwds(:);

end
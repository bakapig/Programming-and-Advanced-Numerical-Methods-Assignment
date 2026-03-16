% Inputs :
% fwdCurve : forward curve data
% T: time to expiry of the option
% cps: vetor if 1 for call , -1 for put
% deltas : vector of delta in absolute value (e.g. 0.25)
% vols : vector of volatilities
% Output :
% curve : a struct containing data needed in getSmileK
function [ curve ] = makeSmile(fwdCurve, T, cps, deltas, vols)

    n = numel(vols);
    if n < 2
        error('makeSmile:TooFewMarks. At least two smile marks are required.');
    end
    if numel(cps) ~= n || numel(deltas) ~= n
        error('makeSmile:SizeMismatch. cps, deltas and vols must have the same length.');
    end
    if ~(isscalar(T) && isnumeric(T) && isreal(T) && isfinite(T) && T > 0)
        error('makeSmile:InvalidMaturity. T must be a finite strictly positive real scalar.');
    end
    if any(~isfinite(cps)) || any(cps ~= 1 & cps ~= -1)
        error('makeSmile:InvalidOptionType. cps must contain only +1 for calls or -1 for puts.');
    end
    if any(~isfinite(deltas)) || any(deltas <= 0 | deltas >= 1)
        error('makeSmile:InvalidDelta. deltas must contain only values strictly between 0 and 1.');
    end
    if any(~isfinite(vols)) || any(vols <= 0)
        error('makeSmile:InvalidVolatility. vols must contain only finite strictly positive values.');
    end

    % 1. We now calculate the forward spot INSIDE the function!
    fwd = getFwdSpot(fwdCurve, T);

    % Hint 1: Assert vector dimension match
    assert(length(cps) == length(vols) && length(vols) == length(deltas), ...
        'Input vectors must have the same length!');

    % Hint 2: Resolve strikes using your delta function
    % (Make sure the order matches your getStrikeFromDelta inputs: fwd, T, cp, sigma, delta)
    Ks = getStrikeFromDelta(fwd, T, cps, vols, deltas);
    
    % Sort strikes to ensure strictly increasing order for the spline
    [Ks, sort_idx] = sort(Ks);
    vols = vols(sort_idx);

    % Hint 3: Check arbitrages (using dummy strike K0 = 0)
    % For K=0, the Black call price limit is C(0) = fwd (see PDF section 1.4)
    % We must NOT call getBlackCall(fwd, T, 0, 0) because log(0) is undefined
    C_K0 = fwd;
    C_Ks = getBlackCall(fwd, T, Ks, vols);
    C_all = [C_K0; C_Ks(:)];
    K_all = [0; Ks(:)];
    
    % Arbitrage Check 1: Call prices must be monotonically decreasing
    dC = diff(C_all);
    assert(all(dC <= 0), 'Arbitrage Violation: Call prices must decrease.');
    
    % Arbitrage Check 2: Call prices must be convex (slopes must be increasing)
    dK = diff(K_all);
    slopes = dC ./ dK;
    assert(all(slopes >= -1) && all(slopes <= 0), 'Arbitrage Violation: Slopes out of bounds.');
    assert(all(diff(slopes) >= -1e-6), 'Arbitrage Violation: Call prices are not convex.');

    % Hint 4: Compute spline coefficients
    pp = spline(Ks, vols);

    % Hint 5: Compute parameters aL, bL, aR, bR using exact tanh equations
    
    % Get exact 1st derivatives at ends of the spline
    d1_K1 = pp.coefs(1, 3); 
    
    h = Ks(end) - Ks(end-1);
    A_R = pp.coefs(end, 1);
    B_R = pp.coefs(end, 2);
    C_R = pp.coefs(end, 3);
    d1_KN = 3 * A_R * h^2 + 2 * B_R * h + C_R;
    
    % Calculate KL and KR
    KL = Ks(1) * (Ks(1) / Ks(2));
    KR = Ks(end) * (Ks(end) / Ks(end-1));
    
    % Calculate bL and bR using atanh (inverse hyperbolic tangent)
    C_tanh = atanh(sqrt(0.5));
    bL = C_tanh / (Ks(1) - KL);
    bR = C_tanh / (KR - Ks(end));
    
    % Calculate aL and aR
    aL = -d1_K1 / bL;
    aR = d1_KN / bR;

    % Pack everything into the struct (renamed to 'curve' per instructions)
    curve.Ks = Ks(:);
    curve.vols = vols(:);
    curve.pp = pp;
    curve.aL = aL;
    curve.bL = bL;
    curve.aR = aR;
    curve.bR = bR;

end
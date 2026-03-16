% Inputs :
% curve : pre - computed fwd curve data
% T: forward spot date
% Output :
% fwdSpot : E[S(t) | S (0)]
function fwdSpot = getFwdSpot ( curve , T )
    if ~(isstruct(curve) && isfield(curve, 'domCurve') && isfield(curve, 'forCurve') && isfield(curve, 'spot') && isfield(curve, 'tau'))
        error('getFwdSpot:InvalidCurve. curve must be a struct created by makeFwdCurve.');
    end
    if ~(isnumeric(T) && isreal(T) && ~isempty(T))
        error('getFwdSpot:InvalidMaturity. T must be a non-empty real numeric array.');
    end
    if any(~isfinite(T(:))) || any(T(:) < 0)
        error('getFwdSpot:InvalidMaturity. T must contain only finite non-negative maturities.');
    end

    if isfield(curve, 'domIntTau')
        domIntTau = curve.domIntTau;
    else
        domIntTau = getRateIntegral(curve.domCurve, curve.tau);
    end
    if isfield(curve, 'forIntTau')
        forIntTau = curve.forIntTau;
    else
        forIntTau = getRateIntegral(curve.forCurve, curve.tau);
    end

    % 1. Get the integral of the domestic rate (r) from 0 to tau, and 0 to T+tau
    domInt_tau = getRateIntegral(curve.domCurve, curve.tau);
    domInt_T_tau = getRateIntegral(curve.domCurve, T + curve.tau);
    
    % 2. Get the integral of the foreign rate (y) from 0 to tau, and 0 to T+tau
    forInt_tau = getRateIntegral(curve.forCurve, curve.tau);
    forInt_T_tau = getRateIntegral(curve.forCurve, T + curve.tau);
    
    % 3. Calculate the integral specifically for the window [tau, T+tau]
    dom_integral = domInt_T_tau - domInt_tau;
    for_integral = forInt_T_tau - forInt_tau;
    
    % 4. Compute the forward spot price G_0(T)
    fwdSpot = curve.spot .* exp(dom_integral - for_integral);

end
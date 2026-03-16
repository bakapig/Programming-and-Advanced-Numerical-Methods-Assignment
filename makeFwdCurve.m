% Inputs :
% domCurve : domestic IR curve data
% forCurve : domestic IR curve data
% spot : spot exchange rate
% tau: lag between spot and settlement
% Output :
% curve : a struct containing data needed by getFwdSpot
function curve = makeFwdCurve ( domCurve , forCurve , spot , tau )

    if ~(isstruct(domCurve) && isfield(domCurve, 'ts') && isfield(domCurve, 'cumInt'))
        error('makeFwdCurve:InvalidDomesticCurve. domCurve must be a struct created by makeDepoCurve.');
    end
    if ~(isstruct(forCurve) && isfield(forCurve, 'ts') && isfield(forCurve, 'cumInt'))
        error('makeFwdCurve:InvalidForeignCurve. forCurve must be a struct created by makeDepoCurve.');
    end
    if ~(isscalar(spot) && isnumeric(spot) && isreal(spot) && isfinite(spot) && spot > 0)
        error('makeFwdCurve:InvalidSpot. spot must be a finite strictly positive real scalar.');
    end
    if ~(isscalar(tau) && isnumeric(tau) && isreal(tau) && isfinite(tau) && tau >= 0)
        error('makeFwdCurve:InvalidTau. tau must be a finite non-negative real scalar.');
    end

    % Simply pack the inputs into the output struct
    curve.domCurve = domCurve;
    curve.forCurve = forCurve;
    curve.spot = spot;
    curve.tau = tau;

end
% Inputs :
% curve : pre - computed data about an interest rate curve
% t: time
% Output :
% integ : integral of the local rate function from 0 to t
function integ = getRateIntegral(curve, t)

    % Input validation
    assert(all(t >= 0), 'Time t must be non-negative.');
    
    % Extrapolation limit: allowed up to 30 days beyond last tenor
    maxT = curve.ts(end) + 30/365;
    assert(all(t <= maxT), ...
        sprintf('Extrapolation beyond %.4f (last tenor + 30 days) not allowed.', maxT));

    % 1. Add the origin point (at time 0, the integral of the rate is 0)
    % We use the variables we explicitly cached in makeDepoCurve
    t_nodes = [0; curve.ts];
    int_nodes = [0; curve.cumInt];
    
    % 2. Evaluate the integral at time 't' using linear interpolation.
    % The 'extrap' flag handles keeping the final rate constant beyond the last tenor.
    integ = interp1(t_nodes, int_nodes, t, 'linear', 'extrap');

end



class PID:
    def __init__(
        self,
        Kp=30.0,
        Ki=0.2,
        Kd=400.0,
        T=1,
        control_signal_MAX=100.0,
        control_signal_MIN=-100.0,
    ):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.T = T
        self.control_signal_MAX = control_signal_MAX
        self.control_signal_MIN = control_signal_MIN
        self.reference = 0.0
        self.erro_total = 0.0
        self.previous_error = 0.0

    def update_constants(self, kp, ki, kd):
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd

    def update_reference(self, reference):
        self.reference = reference

    def control(self, actual_measure):

        erro = self.reference - actual_measure

        self.erro_total += erro

        if self.erro_total >= self.control_signal_MAX:
            self.erro_total = self.control_signal_MAX
        elif self.erro_total <= self.control_signal_MIN:
            self.erro_total = self.control_signal_MIN

        delta_error = erro - self.previous_error
        control_signal = (
            (self.Kp * erro)
            + (self.Ki * self.T * self.erro_total)
            + (self.Kd / self.T * delta_error)
        )

        if control_signal >= self.control_signal_MAX:
            control_signal = self.control_signal_MAX
        elif control_signal <= self.control_signal_MIN:
            control_signal = self.control_signal_MIN

        self.previous_error = erro

        return control_signal

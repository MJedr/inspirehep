import React, { Component } from 'react';
import Suggester from '../../../common/components/Suggester';

import withFormItem from '../withFormItem';

class SuggesterField extends Component {
  constructor(props) {
    super(props);
    this.onBlur = this.onBlur.bind(this);
    this.onChange = this.onChange.bind(this);
    this.onSelect = this.onSelect.bind(this);
    this.recordFieldPopulated = false;
  }

  onBlur() {
    const { form, name } = this.props;
    form.setFieldTouched(name, true);
  }

  onChange(value) {
    const { form, name, recordFieldPath } = this.props;
    form.setFieldValue(name, value);

    if (this.recordFieldPopulated) {
      form.setFieldValue(recordFieldPath, null);
      this.recordFieldPopulated = false;
    }
  }

  onSelect(_, selectedOption) {
    const selectedRecordData = selectedOption.result._source;
    const { form, recordFieldPath, pidType } = this.props;
    // TODO: only send control_number to backend, and create the $ref url there.
    const $ref = `${window.location.origin}/api/${pidType}/${
      selectedRecordData.control_number
    }`;
    form.setFieldValue(recordFieldPath, { $ref });
    this.recordFieldPopulated = true;
  }

  render() {
    const { recordFieldPath, ...restProps } = this.props;
    return (
      <Suggester
        {...restProps}
        data-test-type="suggester"
        onBlur={this.onBlur}
        onChange={this.onChange}
        onSelect={this.onSelect}
      />
    );
  }
}

export default withFormItem(SuggesterField);

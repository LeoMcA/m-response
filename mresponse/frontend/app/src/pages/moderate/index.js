import { connect } from 'react-redux'
import { push } from 'connected-react-router'

import { getCurrentResponse, getProfile } from '@redux/selectors'
import { fetchNextResponse, updateCurrentModeration, submitModeration, skipResponse } from '@redux/actions'
import { DASHBOARD_URL } from '@utils/urls'
import ModeratePage from './moderate'

const mapStateToProps = state => ({
  response: getCurrentResponse(state),
  profile: getProfile(state)
})
const mapDispatchToProps = (dispatch, props) => ({
  back: () => dispatch(push(DASHBOARD_URL)),
  fetchNextResponse: cb => dispatch(fetchNextResponse(cb)),
  onModerationUpdate: ({ criteria }) => dispatch(updateCurrentModeration({
    'positive_in_tone': criteria.positive,
    'addressing_the_issue': criteria.relevant,
    'personal': criteria.personal,
    'submitted_at': Date.now()
  })),
  submitModeration: cb => dispatch(submitModeration(cb)),
  skipResponse: () => dispatch(skipResponse())
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ModeratePage)
